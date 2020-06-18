"""Credit: github.com/alleninstitute/aisynphys
"""
import os, time, datetime
from urllib.request import Request, urlopen
import numpy as np
from progressbar import ProgressBar


def iter_download_with_resume(url, file_path, timeout=10, chunksize=1000000):
    """
    Performs a HTTP(S) download that can be restarted if prematurely terminated.
    The HTTP server must support byte ranges.
    
    Credit: https://gist.github.com/mjohnsullivan/9322154

    Parameters
    ----------
    url : str
        The URL to download
    file_path : str
        The path to the file to write to disk
        
    """
    if os.path.exists(file_path):
        raise Exception("Destination file already exists: %s" % file_path)
    
    file_size = get_url_download_size(url)
    
    tmp_file_path = file_path + '.part_%d'%file_size

    conn = None    
    while True:
        first_byte = os.path.getsize(tmp_file_path) if os.path.exists(tmp_file_path) else 0
        
        try:
            if conn is None:
                # create the request and set the byte range in the header
                req = Request(url)
                req.headers['Range'] = 'bytes=%s-%s' % (first_byte, file_size-1)
                conn = urlopen(req, timeout=timeout)

            while True:
                data_chunk = conn.read(chunksize)
                if len(data_chunk) == 0:
                    break
                    
                # Read the data from the URL and write it to the file
                # (assume that writing is much faster than reading; otherwise this should be done in the background)
                with open(tmp_file_path, 'ab') as fh:
                    fh.write(data_chunk)
                    
                first_byte += len(data_chunk)
                yield (first_byte, file_size, None)
            
        except Exception as exc:
            err = '; '.join(traceback.format_exception_only(type(exc), exc))
            yield (first_byte, file_size, err)
            time.sleep(1)
            conn = None
            continue
        
        
        if first_byte >= file_size:
            break
    
    tmp_size = os.path.getsize(tmp_file_path)
    if tmp_size != file_size:
        raise Exception("Downloaded file %s size %s is not the expected size %s" % (tmp_file_path, tmp_size, file_size))
        
    os.rename(tmp_file_path, file_path)


def get_url_download_size(url):
    file_size = int(urlopen(url).info().get('Content-Length', None))
    if file_size is None:
        raise Exception('Error getting Content-Length from server: %s' % url)
    return file_size


def interactive_download(url, file_path, **kwds):
    """Download a file with periodic updates to the user.
    
    If a Qt application is present, then a progress dialog is displayed. 
    Otherwise, print updates to the console if it appears to be a TTY.
    
    Will attempt to resume downloading partial files.
    """

    message = "Downloading %s =>\n  %s" % (url, os.path.abspath(file_path))

    # get size first just to verify server is listening and the file exists
    size = get_url_download_size(url)
    size_str = si_format(size, suffix='B')

    with ProgressBar(message, 1) as prg_bar:
        prg_bar.maximum = size

        last_update = time.time()
        last_size = None
        n_chunks = 0
        byte_rate = 0
        integration_const = 1.0
        
        for i, size, err in iter_download_with_resume(url, file_path, **kwds):
            now = time.time()
            complete_str = si_format(i, suffix='B', float_format='f', precision=2)
            total_str = si_format(size, suffix='B', float_format='f', precision=1)
            if err is None:
                if last_size is not None:
                    chunk_size = i - last_size
                    dt = now - last_update
                    byte_rate = (chunk_size / dt) ** integration_const * byte_rate ** (1.0 - integration_const)
                    # slower integration as more samples have been collected
                    integration_const = max(1e-3, 1.0 / n_chunks)
                n_chunks += 1
                last_update = now
                last_size = i

                if byte_rate == 0:
                    est_time_str = ""
                else:
                    est_time = (size - i) / byte_rate
                    est_time_str = str(datetime.timedelta(seconds=int(est_time)))

                rate_str = si_format(byte_rate, suffix='B/s', float_format='f')

                stat_str = '%0.2f%% (%s / %s)  %s  %s remaining' % (100.*i/size, complete_str, total_str, rate_str, est_time_str)
            else:
                stat_str = '%0.2f%% (%s / %s)  [stalled; retrying...] %s' % (100.*i/size, complete_str, total_str, err)
            prg_bar.update(value=i, status=stat_str)



SI_PREFIXES = u'yzafpnµm kMGTPEZY'
SI_PREFIXES_ASCII = 'yzafpnum kMGTPEZY'

    
def si_scale(x, min_val=1e-25, allow_unicode=True):
    """
    Return the recommended scale factor and SI prefix string for x.
    
    Example::
    
        si_scale(0.0001)   # returns (1e6, 'μ')
        # This indicates that the number 0.0001 is best represented as 0.0001 * 1e6 = 100 μUnits
    
    credit: pyqtgraph
    """
    try:
        if np.isnan(x) or np.isinf(x):
            return(1, '')
    except:
        print(x, type(x))
        raise
    if abs(x) < min_val:
        m = 0
        x = 0
    else:
        m = int(np.clip(np.floor(np.log(abs(x))/np.log(1000)), -9.0, 9.0))
    
    if m == 0:
        pref = ''
    elif m < -8 or m > 8:
        pref = 'e%d' % (m*3)
    else:
        if allow_unicode:
            pref = SI_PREFIXES[m+8]
        else:
            pref = SI_PREFIXES_ASCII[m+8]
    p = .001**m
    
    return (p, pref)    


def si_format(x, precision=3, suffix='', float_format='g', space=True, error=None, min_val=1e-25, allow_unicode=True):
    """
    Return the number x formatted in engineering notation with SI prefix.
    
    Example::
        si_format(0.0001, suffix='V')  # returns "100 μV"
    
    credit: pyqtgraph
    """
    
    if space is True:
        space = ' '
    if space is False:
        space = ''
    
    (p, pref) = si_scale(x, min_val, allow_unicode)
    if not (len(pref) > 0 and pref[0] == 'e'):
        pref = space + pref
    
    if error is None:
        fmt = "%." + str(precision) + float_format + "%s%s"
        return fmt % (x*p, pref, suffix)
    else:
        if allow_unicode:
            plusminus = space + u"±" + space
        else:
            plusminus = " +/- "
        fmt = "%." + str(precision) + float_format + "%s%s%s%s"
        return fmt % (x*p, pref, suffix, plusminus, si_format(error, precision=precision, suffix=suffix, space=space, min_val=min_val))

