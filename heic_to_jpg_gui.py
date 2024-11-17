#!/usr/bin/python3.10
from functools import reduce
from multiprocessing import Process, Queue
import PySimpleGUI as sg
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
count_debug_files = 250


def get_file_count(curr_paths: list[str]) -> int:
    count = 0
    for path in curr_paths:
        if os.path.isdir(path):
           count += len(list(filter(lambda file: file.lower().endswith(".heic"),os.listdir(path))))
        elif os.path.basename(path).lower().endswith(".heic"):
            count += 1
    return count

def filter_images(files:list[str])->list[str]:
    return list(filter(lambda img: img.lower().endswith(".heic"),files))

def print_conversion_result(num_files_to_convert: int, num_files_converted: int,):

    subs_file = num_files_to_convert-num_files_converted
    if subs_file > 0:
        print(
            f"Converted {num_files_converted} files - {subs_file} remaining")

def conversion_process(images:list[str],curr_path:str,queue:Queue,type:str):
    num_files_converted = 0
    for filename in images:
            try:
                heic_img = pillow_heif.read_heif(os.path.join(curr_path,filename))
                img = Image.frombytes(
                    heic_img.mode, heic_img.size, heic_img.data, "raw")
            except Exception as e:
                print(f"Error converting {os.path.join(curr_path,filename)}:",e)
            else: 
                new_file = Path(filename).stem +'.'+type
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


def convert_files_for_path(curr_path:str, type:str,step_print:int):
    num_files_converted = 0
    if not no_folders:
        os.makedirs(os.path.join(curr_path,heic_folder), exist_ok=True)
    print(f"Starting conversion from HEIC to {type.upper()}")
    images = filter_images(os.listdir(curr_path))   
    num_files_to_convert = images.__len__()
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
            proc = Process(target=conversion_process, args=(dic[i],curr_path,q,type))
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()
        
        step_count = 1
        while not q.empty() :
            num_files_converted+= q.get_nowait()
            if num_files_converted >= (step_print*step_count):
                print_conversion_result(num_files_to_convert,num_files_converted)
                step_count+=1
    except PermissionError as e:
        print("Not enough permissions operate:",e)
    except Exception as e:
        print("An error has occured:",e)
    finally:
        if not no_folders:
            if (not os.listdir(os.path.join(curr_path,heic_folder))):
                os.rmdir(os.path.join(curr_path,heic_folder))
        print(
            f"Finished converting {num_files_converted} images in {curr_path} from HEIC to {type.upper()}\n")
    return num_files_converted

def convert_files_for_sing_file(curr_file:str, type:str):
    curr_path = os.path.dirname(curr_file)
    filename = os.path.basename(curr_file)
    num_files_converted = 0

    if not no_folders:
        os.makedirs(os.path.join(curr_path,heic_folder), exist_ok=True)
    print(f"Starting conversion from HEIC to {type.upper()}")
    image = curr_file if filename.lower().endswith(".heic") else ""  
    if image != "":
        try:
            heic_img = pillow_heif.read_heif(image)
            img = Image.frombytes(
                heic_img.mode, heic_img.size, heic_img.data, "raw")
        except Exception as e:
            print(f"Error converting {curr_file}:",e)
        else: 
            new_file = Path(image).stem +'.'+type
            new_path_for_file = os.path.join(curr_path,(new_file))
            try: 
                img.save(f"{new_path_for_file}")
            except Exception as e:
                print(f"Error while trying to save {new_path_for_file}:",e)
            if not no_folders:
                try:
                    shutil.move(os.path.join(curr_path,filename),
                                os.path.join(curr_path,heic_folder))
                except shutil.Error as e:
                    print(f"Couldn't move {os.path.join(curr_path,filename)} to {os.path.join(curr_path,heic_folder)}:",e)
            num_files_converted = 1
        print(
            f"Finished converting {filename} from HEIC to {type.upper()}\n")
    return num_files_converted

def convert_files(curr_paths: list[str], conv_type: str,step_print:int):
    num_files_converted = 0
    print(f"Paths searched for conversion: {curr_paths}")
    for path in curr_paths:
        if os.path.isfile(path):
            if os.path.basename(path).lower().endswith(".heic"):
                num_files_converted += convert_files_for_sing_file(path,conv_type)
        elif os.path.isdir(path):
            num_files_converted += convert_files_for_path(path,conv_type,step_print)
        else:
            print(f"{path} is not a directory nor an HEIC file")
    print(f"Converted in total: {num_files_converted} images from HEIC to {conv_type.upper()}")


if __name__ == "__main__":

    # All the stuff inside your window.
    file_listing_column = [  
        [sg.Text("Select one or multiple files/folders to convert"),
                 sg.Button('Convert')],
                 [sg.Input(key="browse main"), 
                  sg.Button(key="browse main", button_text="Current Folder")],
                [sg.Listbox(values=[],enable_events=True,size=(40,10),key="'-INPUT-'"),sg.Input(key="files"), 
                sg.FilesBrowse(key="'files",button_text="Browse Files"),
                sg.FolderBrowse()]
                ]

    layout = [
        [
            sg.Column(file_listing_column)
        ]
    ]
    # Create the Window
    window = sg.Window('HEICON — HEIC image converter', layout)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()

        # if user closes window or clicks cancel
        if event == sg.WIN_CLOSED:
            break
        if event == "browse main":
            files = sg.popup_get_file('Select one or multiple folders')
            print("browsing...")
     

    window.close()
    # parser = argparse.ArgumentParser(prog="HEIC-to-JPG",
    #                                  description="Convert those pesky HEIC images to JPG or other formats")
    # parser.add_argument(
    #     "--nr", help="Disables the creation of the folder containing the HEIC images after conversion", action="store_true")
    # parser.add_argument(
    #     "--debug", help="For debugging the app", action="store_true")
    # parser.add_argument("--type", default="jpg",
    #                     help="Defines the type to convert to (Default: jpg)", choices=convert_types)
    # parser.add_argument("--path", default=".", nargs='+',
    #                     help="Specify one or multiple paths of either folders or files to convert")
    # parser.add_argument("--np",default=75,help="Specify the number of processes to use in multiprocessing (Default: 75)",type=int)
    # args = parser.parse_args()

    # no_folders = args.nr
    # debug_mode = args.debug
    # conv_type : list[str]= args.type
    # conv_path = args.path
    # num_procs = args.np

        
    # conv_path = [" "] + conv_path
    # checked_paths : str = reduce(lambda acc,path: acc if os.path.exists(path) else acc + " "+path,conv_path).strip()

    # if debug_mode:
    #     conv_path = "./debug"
    #     os.makedirs(conv_path, exist_ok=True)
    #     try:
    #         for i in range(0, count_debug_files):
    #             shutil.copy(f"{conv_path}/../debug_resources/sample1.heic",
    #                         f"{conv_path}/sample_"+str(i)+".heic")
    #     except:
    #         print("Debug files already present")

    # if checked_paths == "" or debug_mode:
    #     num_files_to_convert = get_file_count(conv_path) if not debug_mode else count_debug_files
    #     conv_path = conv_path[1:]
    #     num_procs = num_files_to_convert if num_procs > num_files_to_convert else num_procs
    #     print(f"Found {num_files_to_convert} files to convert")
    #     if num_files_to_convert > 0:
    #         step_print = round(num_files_to_convert*percent_print)
    #         if step_print <= 0:
    #             step_print = 1
    #         time_start = time.time()
    #         if debug_mode:
    #             print("DEBUG MODE")
    #             conv_path = ["debug/"]
    #             convert_files(conv_path,conv_type,step_print)
    #         else:
    #             convert_files(conv_path, conv_type,step_print)
    #         print(f"Took {time.time()-time_start} seconds")
    # else:
    #     print(f"The path(s): \"{checked_paths}\" doesn't or don't exist")
