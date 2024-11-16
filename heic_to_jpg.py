#!/usr/bin/python3.10
from multiprocessing import Process, Queue
import os
import argparse
import shutil
import pillow_heif
from PIL import Image
from pathlib import Path
import time
heic_folder = "heic_files"
no_folders = False
debug_mode = False
percent_print = 0.25
step_print = 25
convert_types = ["jpg", "png"]
conv_path = "."
num_procs = 75


def get_file_count(curr_path: str) -> int:
    return len(list(filter(lambda file: file.lower().endswith(".heic"),os.listdir(curr_path))))

def filter_images(files:list[str])->list[str]:
    return list(filter(lambda img: img.lower().endswith(".heic"),files))

def print_conversion_result(num_files_to_convert: int, num_files_converted: int,):

    subs_file = num_files_to_convert-num_files_converted
    if num_files_converted % step_print == 0 and subs_file > 0:
        print(
            f"Converted {num_files_converted} files - {subs_file} remaining")

def conversion_process(images:list[str],curr_path:str,queue:Queue):
    num_files_converted = 0
    for filename in images:
            try:
                heic_img = pillow_heif.read_heif(os.path.join(curr_path,filename))
                img = Image.frombytes(
                    heic_img.mode, heic_img.size, heic_img.data, "raw")
            except Exception as e:
                print(f"Error converting {os.path.join(curr_path,filename)}:",e)
            else: 
                new_file = Path(filename).stem +'.'+conv_type
                try: 
                    img.save(f"{os.path.join(curr_path,(new_file))}")
                except Exception as e:
                    print(f"Error while trying to save {os.path.join(curr_path,(new_file))}:",e)
                if not no_folders:
                    try:
                        shutil.move(os.path.join(curr_path,filename),
                                    os.path.join(curr_path,heic_folder))
                    except shutil.Error as e:
                        print(f"Couldn't move {os.path.join(curr_path,filename)} to {os.path.join(curr_path,heic_folder)}:",e)
                num_files_converted += 1
    queue.put(num_files_converted)


def convert_files(curr_path: str, conv_type: str):
    num_files_converted = 0
    final_type = conv_type.replace('.', "").upper()
    if not no_folders:
        os.makedirs(os.path.join(curr_path,heic_folder), exist_ok=True)
    print(f"Starting conversion from HEIC to {conv_type.upper()}")
    images = filter_images(os.listdir(curr_path))   
    try:
        dic = {}
        q = Queue()
        processes :list[Process] = []
        for i in range(num_procs):
            temp = []
            for id,elem in enumerate(images):
                if id % num_procs == i:
                    temp.append(elem)
            dic[i] = temp.copy()
        for i in range(num_procs):
            proc = Process(target=conversion_process, args=(dic[i],curr_path,q))
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()
        
        while not q.empty() :
            num_files_converted+= q.get_nowait()
    except PermissionError as e:
        print("Not enough permissions operate:",e)
    except Exception as e:
        print("An error has occured:",e)
    finally:
        if not no_folders:
            if (not os.listdir(os.path.join(curr_path,heic_folder))):
                os.rmdir(os.path.join(curr_path,heic_folder))
        print(
            f"Finished converting {num_files_converted} images from HEIC to {final_type}")
    return num_files_converted


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="HEIC-to-JPG",
                                     description="Convert those pesky HEIC images to JPG or other formats")
    parser.add_argument(
        "--nr", help="Disables the creation of the folder containing the HEIC images after conversion", action="store_true")
    parser.add_argument(
        "--debug", help="For debugging the app", action="store_true")
    parser.add_argument("--type", default="jpg",
                        help="Defines the type to convert to (Default: jpg)", choices=convert_types)
    parser.add_argument("--path", default=".",
                        help="Specify a path to convert files at")
    parser.add_argument("--np",default=75,help="Specify the number of processes to use in multiprocessing",type=int)
    args = parser.parse_args()

    no_folders = args.nr
    debug_mode = args.debug
    conv_type = args.type
    conv_path = args.path
    num_procs = args.np

        
    

    if debug_mode:
        conv_path = "./debug"
        os.makedirs(conv_path, exist_ok=True)
        try:
            for i in range(0, 250):
                shutil.copy(f"{conv_path}/../debug_resources/sample1.heic",
                            f"{conv_path}/sample_"+str(i)+".heic")
        except:
            print("Debug files already present")

    if os.path.exists(conv_path):
        num_files_to_convert = get_file_count(conv_path)
        num_procs = num_files_to_convert if num_procs > num_files_to_convert else num_procs
        print(f"Found {num_files_to_convert} files to convert")
        if num_files_to_convert > 0:
            step_print = round(num_files_to_convert*0.10)
            if step_print <= 0:
                step_print = 1
            time_start = time.time()
            if debug_mode:
                print("DEBUG MODE")
                conv_path = "debug/"
                convert_files(conv_path,conv_type)
            else:
                convert_files(conv_path, conv_type)
            print(f"Took {time.time()-time_start} seconds")
    else:
        print(f"{conv_path} doesn't exist")
