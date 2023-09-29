Problem statement: USING gRPC TO CREATE CLIENT SERVER MODEL TO SIMULATE MISSILE STRIKE ON BATTLEFIELD. 

Group Details:
1.	BUNTY AGARWAL      (2023H1030090P)
2.	APURAV DESHMUKH (2023H1030096P)

Overview

In this project, we have developed a simulation of a battlefield scenario where soldiers and a commander utilize a client-server model implemented using gRPC (Google Remote Procedure Call) to simulate missile strikes and the defense actions of soldiers. 

Tech Stack:

 1.	RPC Framework - gRPC
 2.     Programming Language: Python 
 3.     Version Control: Git
 
## Instructions to Run the Code :

Step 1:  pip install grpcio

Step 2:  pip install grpc-tools

Step 3:  pip install colorama  (for printing coloured text on terminal)

Command to genarete the protobuf file : 

Step 3:  python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. soldier.proto 

Command to run server and client file (NOTE: Please run Server command before running client command ) :

Step 4: Change the address of server in client.py global variable SERVER_ADDRESS as required

Step 5:  python server.py

Step 6:  python client.py

After executing the client.py file it will ask for the inputs from the user , example as shown below :

bunty@LAPTOP-B1F5FA3J:/mnt/f/grpc/Test$ python3 client.py
 
Enter number of soldiers : 10
Enter size of the field : 10
Enter duration of battle T : 30
Enter missile interval t : 5

Now the user can enter the programmable inputs accordingly.

GITHUB REPO LINK : https://github.com/ApuravDeshmukh2309/AOS_Assignment1.git
