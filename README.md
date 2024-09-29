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
-	When select the metrics to monitor your server performance, always select the ones that’s important to your organization. In my case, the most important metrics that I care the most are the CPG Usage, Data Read from the server, and the Lagging Times that we replicate data from Master server to slave1 and slave 2 server.
-	For Continuous Development (CD) and Continuous Integration (CI) in real work cases, it’s better to use Docker to isolate our application can run in its own container, allowing for isolated testing and development without conflict. In my case, my system does not support Docker. 


# Step 1: Prepare Local Environment
## 1.1 Install Grafana locally
Per the guidance of the Grafana Labs, download the Installer to my local Windows system. Here is the official url where you can download the Grafana:
https://grafana.com/docs/grafana/latest/setup-grafana/installation/windows/
Grafana download page:
https://grafana.com/grafana/download?platform=windows

Since my system is Windows system, I’m going to download Windows Installer:
![Step 1 1 Image 1](https://github.com/user-attachments/assets/b8e46b1c-30e2-4050-9335-6f4ae8f7a387)

