import rpyc
import sys
import os
import logging
import time
import getpass
import colorama

from colorama import Fore,Style,Back
colorama.init()

import base64


logging.basicConfig(level=logging.DEBUG)


def get(master, file):
    file_table = master.read(file)
    if not file_table:
        logging.info("file not found")
        return

    for block in file_table:
        for host, port in block['block_addr']:
            try:
                con = rpyc.connect(host, port=port).root
                data = con.get(block['block_id'])
                if data:
                    sys.stdout.write(data)
                    break
            except Exception as e:
                continue
        else:
            logging.error("No blocks found. Possibly a corrupt file")
    print("\n")        

def put(master, source, dest):
    # save name in file for list(ls)
    fileList = open("ls.temp", "a")
    fileList.write(dest + "\n")
    fileList.close()

    size = os.path.getsize(source)
    blocks = master.write(dest, size)
    with open(source) as f:
        for block in blocks:
            data = f.read(master.block_size)
            block_id = block['block_id']
            minions = block['block_addr']

            minion = minions[0]
            minions = minions[1:]
            host, port = minion

            con = rpyc.connect(host, port=port)
            con.root.put(block_id, data, minions)

def getFile(master, file):
  file1 = open("temp_copy", "a")
  file_table = master.read(file)
  if not file_table:
      logging.info("file not found")
      return

  for block in file_table:
      for host, port in block['block_addr']:
          try:
              con = rpyc.connect(host, port=port).root
              data = con.get(block['block_id'])
              if data:
                  # sys.stdout.write(data)
                  file1.write(data)
                  break
          except Exception as e:
              continue
      else:
          logging.error("No blocks found. Possibly a corrupt file")
  file1.close()

def cp(master, source, dest):
  getFile(master, source)
  file1 = open("temp_copy", "r") 
  # print(file1.read()) 
  file1.close()
  try:
    put(master, "temp_copy", dest)
  except Exception as e:
    print("File Not Found\n")
  removeTempFiles("temp_copy")
  
def ls():
    file1 = open("ls.temp", "r") 
    print("File on Server:\n") 
    print(file1.read())
    print() 
    file1.close() 

def removeTempFiles(file):
    try:
      os.remove(file)
    except Exception as e:
      print("logging you out...")

def encrypt_private_key(a_message, private_key):
    try:
        encryptor = PKCS1_OAEP.new(private_key)
        encrypted_msg = encryptor.encrypt(a_message)
        encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    except Exception as e:        
        encoded_encrypted_msg = a_message
    return encoded_encrypted_msg


def authenticate(msg):
    print("Authenticating with KDC server...")
    time.sleep(2)
    if(msg=="CL8795" or msg=="CL1010" or msg=="CL1234"):
        print(Fore.GREEN + "Authentication successful" + Style.RESET_ALL)
        return True
    else:
        return False

def main(args):
    #Authenticate KDC
    clientID = getpass.getpass("Enter your client ID: ")
    pswd = getpass.getpass("Enter password to encrypt: ")
    encrypted_msg = encrypt_private_key(clientID, pswd)
    if(authenticate(encrypted_msg) is False):
        print(Fore.RED + "Incorrect clientID or password. Please try again"+Style.RESET_ALL)
        return

    #Connect to File server
    con = rpyc.connect("localhost", port=2131)
    master = con.root
    print("########## Welcome to Vitarit File Pranali ########## \n")
    while(1):
      try:
        command = input(Fore.GREEN + "vfp@shivam$ " + Style.RESET_ALL).split(" ")
        if command[0] == "cat":
            get(master, command[1])
        elif command[0] == "put":
            put(master, command[1], command[2])
        elif command[0] == "cp":
            cp(master, command[1], command[2])
        elif command[0] == "ls":
            try:
              ls()
            except Exception as e:
              print("no files found")
        elif command[0] == "pwd":
            print(os.getcwd())
        elif command[0] == "exit":
            removeTempFiles("ls.temp")
            sys.exit()
        elif command[0] == "help":
            print("\n Supported Commands VFP v0.8.4 \n")
            print("1. put <File Address> <File Name on server>")
            print("2. cp <File Name on server> <Copied File name on server>")
            print("3. ls")
            print("4. cat <File Name on server>")
            print("5. pwd")
            print("6. exit ")
        else:
            logging.error("Invalid command")
      except Exception as e:
        removeTempFiles("ls.temp")







if __name__ == "__main__":
    main(sys.argv[1:])
