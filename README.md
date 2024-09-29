# MySQL Server Grafana Metric Monitoring

## Project Goal
- Set up a MySQL cluster with 1 master and 2 slaves on your local machine.

## Project Bonus
-	Set up Grafana to monitor the MySQL cluster.
	Add a small load testing script to generate traffic on the cluster.
	
## Project Objective 
Understand the underlying database concepts and mechanisms.

## My Initiatives
- Use MySQL Server 5.7 to set up the cluster locally.
-	Install Grafana locally and monitor the cluster through localhost:9090.
-	Use Prometheus and MySQL Exporter (there is no available MYSQL Exporter for my Windows system, so we’ll simulate the metrics collection by using built-in MySQL performance schema and custom python scripts for the Exporter) to collect cluster metrics.
-	Write a Python File to simulate the real data load to the cluster.
-	For command prompt and python code developing, I’m going to combine with Visual Studio Code locally to develop my codes.
-	For the testing dataset, I created a table under the replicated_db database called Users (you can find the table’s schema below in step 4.3)

## Lessons Learned 
-	Create a project folder to include all your project files in an appropriate directory, remember to make sure the directory is correct in your configuration files.
-	When running your project Python script, it’s always recommended to create a separate Virtual Environment under your project folder.
-	When select the metrics to monitor your server performance, always select the ones that’s important to your organization. In my case, the most important metrics that I care the most are the CPU Usage, Data Read from the server, and the Lagging Times that we replicate data from Master server to slave1 and slave 2 server.
-	For Continuous Development (CD) and Continuous Integration (CI) in real work cases, it’s better to use Docker to isolate our application can run in its own container, allowing for isolated testing and development without conflict. In my case, my system does not support Docker. 
- For data privacy security concern, if we deploy the codes on cloud platform like AWS, we will need to be pretty careful about the password we use for the server. Try to set up a env file to include the password instead, and try to set up specific IAM rule to limit the access of the files we've deployed.

# Step 1: Prepare Local Environment
## 1.1 Install Grafana locally
Per the guidance of the Grafana Labs, download the Installer to my local Windows system. Here is the official url where you can download the Grafana:
https://grafana.com/docs/grafana/latest/setup-grafana/installation/windows/
Grafana download page:
https://grafana.com/grafana/download?platform=windows

Since my system is Windows system, I’m going to download Windows Installer:

![Step 1 1 Image 1](https://github.com/user-attachments/assets/b8e46b1c-30e2-4050-9335-6f4ae8f7a387)

I’m going to install Grafana under the path of C:\Program Files\GrafanaLabs\, which is the standard default path of the installer:

![Step 1 1 Image 2](https://github.com/user-attachments/assets/2a107c7d-13a5-45d9-836a-c13810f9b012)

Once the Grafana is installed, go to localhost:3000 in the browser:

![Step 1 1 Image 3](https://github.com/user-attachments/assets/54fbf6ca-b44c-47c8-b295-702f7e44c333)

Log in Grafana using the default username (admin) and password (admin), and change the password once using the default one to log in:

![Step 1 1 Image 4](https://github.com/user-attachments/assets/458da74f-d81f-4e0e-85a2-3f0046aa2f43)

Now we have successfully installed and logged in to our Grafana and it’s ready to be used later:

![Step 1 1 Image 5](https://github.com/user-attachments/assets/5be96a83-3e05-4dcf-b39a-ced15a9bbb5e)

# Step 2: Set up MySQL cluster with master and slaves
## 2.1 Create folders in MySQL directory for master and the 2 slaves

![Step 2 1 Image 1](https://github.com/user-attachments/assets/7615c2db-c7cb-49a0-b541-926ba0d8f7ff)

## 2.2 Create Servers
Copy bin and share folders from your original MySQL instance into each of the new folders we just created

![Step 2 2 Image1](https://github.com/user-attachments/assets/13786ee5-677f-460b-b182-18b29e08b701)
![Stpe 2 2 Image2](https://github.com/user-attachments/assets/e2f917a2-3079-4800-913d-bcea8acde2b4)
![Stpe 2 2 Image3](https://github.com/user-attachments/assets/023adea6-3de1-44bc-b74c-373644dbd582)

## 2.3 Now we need to configure the Master Server
In the directory of where your master bin is, run the following command in the command line: 
```bash
mysqld --initialize-insecure --console --datadir=C:\Program Files\MySQL\master\data
```
If you encounter a permission issue like this, you will need to run the command line as an administrator.

![Step 2 3 Image1](https://github.com/user-attachments/assets/7c58c9da-5b16-4838-8b18-9bdf7be90e09)

Remember to go to the directory where your sqld.exe file exists. In my case, the file is in C:\Program Files\MySQL\master\bin>:

![Step 2 3 Image2](https://github.com/user-attachments/assets/37ffb9f4-e69f-4836-b301-452cc565130b)

Create the configuration file called my.ini and save it to the master bin folder:

![Step 2 3 Image3](https://github.com/user-attachments/assets/8c6d3c4b-b3fe-46e5-b949-05b9d4c53766)
![Step 2 3 Image4](https://github.com/user-attachments/assets/b7e86057-ecc2-42e8-9803-e542c24b697d)

Run the following command to start the Master Server:
```bash
mysqld --defaults-file="C:\Program Files\MySQL\master\bin\my.ini" --console
```

If you encounter an error like this, saying the port might be in use by another application, you will need to stop the service first:

![Step 2 3 Image5](https://github.com/user-attachments/assets/0a28e7d3-ccc8-4ebf-adb7-99fb6d04e87f)

Hit Windows key + R to open up the Run dialog:

![Step 2 3 Image6](https://github.com/user-attachments/assets/b6ef191c-5fed-498c-a5db-e5171cc9e4ae)

Locate the running MySQL and right click to stop it first:

![Step 2 3 Image7](https://github.com/user-attachments/assets/90e8961b-4d34-4641-a0a8-07336f2a95ea)

Restart the Master Server by running the command:
```bash
mysqld --defaults-file="C:\Program Files\MySQL\master\bin\my.ini" --console
```
![Step 2 3 Image8](https://github.com/user-attachments/assets/f9c829e2-415b-4742-9081-0ab4ce75b98c)

Open a new Command Line window to connect to the master server:

![Step 2 3 Image9](https://github.com/user-attachments/assets/5916c647-274c-4468-b3ab-7fca1c95cb27)

Since I have MYSQL Workbench installed in my system, I can write the SQL queries by connecting to the master server on Workbench (you can use another different GUI if you like to, but this is not necessary, because you can even write SQL queries in the command line):

![Step 2 3 Image10](https://github.com/user-attachments/assets/d9f825ef-bb80-4d26-b851-2c8995172a9d)

Now create a new user and grant access to it for replicating data later:

![Step 2 3 Image11](https://github.com/user-attachments/assets/49637df8-b95d-466e-b6c2-f06ab68d0670)

## 2.4 Now we need to configure the Slave Servers in the command line as well
### Initialize Data Directory
Slave 1:

![Step 2 4 Image1](https://github.com/user-attachments/assets/170a9801-c921-432d-8818-ca7cda5fad20)

Slave2:

![Step 2 4 Image2](https://github.com/user-attachments/assets/413a2d1a-4f29-4f94-a0e9-62580acdcb4b)

### Create Configuration File
Salve1:

![Step 2 4 Image 3](https://github.com/user-attachments/assets/87091764-b61c-4d62-95bf-7b9056b94c84)

Slave2:

![Step 2 4 Image4](https://github.com/user-attachments/assets/2a036fef-0e72-49bf-bad5-502e391876be)

### Start the Slave Servers
Slave1:

![Step 2 4 Image5](https://github.com/user-attachments/assets/4954799b-6fb4-4648-817e-d6f494272565)

Slave2 (Open another new Command window to start the server):

![Step 2 4 Image6](https://github.com/user-attachments/assets/06a99611-9724-4fa8-a323-50e0c21fd5d0)

Now we will be able to connect to three servers including Master, slave 1 and slave 2 on MySQL Workbench:

![Step 2 4 Image7](https://github.com/user-attachments/assets/7338d27f-5c3a-4123-a406-608d84b648f0)

### Let’s configure Replication
Salve1:

First, connect to the slave server on the command line (Run the command line in the slave 1 bin folder. If you are using a GUI, like MySQL Workbench, you don’t need to run this command line, just go to your GUI to connect your server there):
```bash
mysql -u root --port=3307
```

Then execute the following SQL queries to get started the replication:
```bash
ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourRootPassword';
CHANGE MASTER TO
    MASTER_HOST='127.0.0.1',
    MASTER_USER='rep1',
    MASTER_PASSWORD='test1',
    MASTER_LOG_FILE='master-bin.000001',  -- Use the 'File' from master status
    MASTER_LOG_POS=154;                   -- Use the 'Position' from master status
START SLAVE;

```
![Step 2 4 Image8](https://github.com/user-attachments/assets/2f6af539-e19a-4e45-a862-755abd425d2a)

Slave 2:

First, connect to the slave server on the command line (Run the command line in the slave 2 bin folder. If you are using a GUI, you don’t need to run this command line, just go to your GUI to connect your server there):
```bash
mysql -u root --port=3308
```

Then execute the following SQL queries to get started the replication:

```bash
ALTER USER 'root'@'localhost' IDENTIFIED BY 'YourRootPassword';
CHANGE MASTER TO
    MASTER_HOST='127.0.0.1',
    MASTER_USER='rep1',
    MASTER_PASSWORD='test1',
    MASTER_LOG_FILE='master-bin.000001',  -- Use the 'File' from master status
    MASTER_LOG_POS=154;                   -- Use the 'Position' from master status
START SLAVE;
```

![Step 2 4 Image9](https://github.com/user-attachments/assets/8f714ae4-a988-4ef4-8a8b-c99b72c401f2)

## 2.5 Replication Process Verification
Insert some data to test the replication in master server:

![Step 2 4 Image10](https://github.com/user-attachments/assets/cccfd1fd-3bf1-478c-abad-0ffa19b64189)

Verify Data on Slave 1 Server:

![Step 2 5 Image2](https://github.com/user-attachments/assets/6d21efa3-aeb3-48f7-9fc5-f81a2f9dbe73)

Verify data on Slave 2 Server:

![Step 2 5 Image3](https://github.com/user-attachments/assets/a4d25100-74d3-453c-a717-1eafab04bd13)

# Step 3: Set up Grafana for Monitoring
## 3.1 Install Prometheus to local system
url to download Prometheus (I save the downloaded file to C:/Prometheus):
https://prometheus.io/download/

## 3.2 Create an exporter python file
In directory C:/mysql_monitoring, creat a python file called mysql_metrics_exporter.py

![Step 3 2 Image1](https://github.com/user-attachments/assets/bf410581-32b4-4243-9082-ae8590343b2f)

## 3.3 Run the Metrics Exporter
Run the following command in the command line in the directory of the exporter:
```bash
Python mysql_metrics_exporter.py
```

## 3.4 In the directory where you download Prometheus, edit the Prometheus.yml file
In my case, the file is located in C:/Prometheus/Prometheus/Prometheus. It defines how Prometheus scrapes metrics from targets, manages alerting rules, and configures various settings. In my case, I configure my target port to be 8000

![Step 3 4 Image1](https://github.com/user-attachments/assets/cbc67043-8aae-4d52-b662-4a09528c5e63)

![Step 3 4 Image2](https://github.com/user-attachments/assets/f3c21ade-6f6d-4954-b9c2-bab6f241ca47)

Then start Prometheus Server by running the following command line in the directory of Grafana.exe:
```bash
Prometheus.exe –-config.file=Prometheus.yml
```

## 3.5 Add Prometheus Data Source
Select Connection  Data source  Prometheusenter server url: http://localhost:9090 (by default, Prometheus use the port 9090 to connect the Prometheus server, and the port 8000 I’ve configured in my yml file is used by Prometheus to scrape metrics from my target service)

![Step 3 5 Image1](https://github.com/user-attachments/assets/6c356a1e-fcf5-4b54-ae68-45f1497a855e)

# Step 4 Now we load a test dataset using python scripts to generating real-time random data
## 4.1 First we need to create a Virtual Environment to ensure that dependencies are managed separately:
Run the following command in the command line to create a virtual environment
```bash
python -m venv load_test_env
```

## 4.2 Activate the virtual environment
Use the following command to activate the VM (The virtual environment is for us to separate our project from our local environment, which means the libraries we install for this project will be only work for itself once we activate it):
```bash
.\load_test_env\Scripts\Activate
```

## 4.3 Create a load test python script (load_test.py) to generate some random data
Before running the Python script to generate some fake data, make sure you have your table created with this structure in your MySQL Master database, including first_name, last_name, email, and address:

![Step 4 3 Image1](https://github.com/user-attachments/assets/0abf1a51-4a15-4b54-ac4c-8cf2b2cc2159)

Then run the following command to run the script

![Step 4 3 Image2](https://github.com/user-attachments/assets/d1659229-1d3d-4ea4-a8f7-f894a2171992)

# Step 5 Monitor real-time MySQL Metrics
Here I’ve selected 3 metrics on Grafana (You need to go to the url that we specified at the beginning to create a visualization dashboard): 
- mysql_cpu_usage # Current CPU usage percentage of the MySQL server process.
- mysql_innodb_data_read # Total count of data reads from InnoDB.
- mysql_replication_lag_seconds # Time lag in seconds for replication on slave servers.


![Step 5 Image1](https://github.com/user-attachments/assets/a6c54de1-73b7-4c9f-ba19-d64dab1c155e)
