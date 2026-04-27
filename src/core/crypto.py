import fitz
import itertools
import string
import multiprocessing
import time
import sys

def sysprint(text):
    sys.stdout.write(text + '\n')
    sys.stdout.flush()

def check_password_chunk(pdf_path, chunk):
    try:
        doc = fitz.open(pdf_path)
        for pwd in chunk:
            if doc.authenticate(pwd):
                return pwd
        doc.close()
    except Exception:
        pass
    return None

def brute_force_manager(pdf_path, max_length, callback):
    start_time = time.time()
    sysprint(f"=== PDF 암호 돌파 작전 개시 (Max Length: {max_length}) ===")
    
    doc = fitz.open(pdf_path)
    if not doc.needs_pass:
        doc.close()
        callback("암호가 없는 파일이다 게이야.")
        return
    doc.close()

    chars = string.ascii_lowercase + string.digits
    chunk_size = 10000
    cpu_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpu_cores)
    
    found_pwd = None
    
    for length in range(1, max_length + 1):
        if found_pwd: break
        sysprint(f"[{length}자리 패스워드 탐색 중...]")
        
        pwd_generator = (''.join(p) for p in itertools.product(chars, repeat=length))
        
        while True:
            chunk = list(itertools.islice(pwd_generator, chunk_size))
            if not chunk:
                break
            
            chunk_splits = [chunk[i::cpu_cores] for i in range(cpu_cores)]
            results = []
            for split in chunk_splits:
                if split:
                    results.append(pool.apply_async(check_password_chunk, (pdf_path, split)))
            
            for r in results:
                res = r.get()
                if res:
                    found_pwd = res
                    break
                    
            if found_pwd:
                break

    pool.terminate()
    pool.join()
    
    elapsed = time.time() - start_time
    
    if found_pwd:
        msg = f"할렐루야! 뚫었다 이기야!!\n비밀번호: [{found_pwd}]\n소요시간: {elapsed:.2f}초"
    else:
        msg = f"실패... {max_length}자리 이하 영소문자/숫자 중엔 없다 ㅠ\n좌파들의 음모일지도 모름."
        
    callback(msg)
