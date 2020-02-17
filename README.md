# Item Catalog
This project is a full CRUD application that also implements google OAuth. This is an application that provides a list of items within a variety of categories (in this case-Sport) as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items. This application is a RESTful web application built using the Flask Python Framework. It utilizes Google OAuth authentication for users registration and authentication.

## Technologies Implemented
 - RESTful
 - Flask Framework
 - CRUD 
 - HTTP methods
 - Google OAuth authentication
 - Python
 - Javascript/jQuery
 - HTML
 - CSS

## Getting Started
Accessing this application involves having the following tools installed on your computer:
- python
- virtualBox
- Vagrant
- Virtual Machine(VM).
The Vagrant and VirtualBox are used to install and manage the VM. You also need a terminal. You can use the regular terminal if you are on Mac or Linux. For Windows, you can use Git Bash. it can be downloaded [here](https://git-scm.com/downloads)
- Browser (Any browser should work)

### Python Installation
If you are on Linux, you probably already have python installed with your distro. However, to download and install python, follow the instruction [here](https://realpython.com/installing-python/)

### Install VirtualBox
Download VirtualBox from [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1). Install the platform package for your operating system. You do not need to open VirtualBox after installation. Vagrant will do that.

### Install Vagrant
Download Vagrant from [here](https://www.vagrantup.com/). Vagrant configures the VM and lets you share files between your host computer and the VM'S filesystem. Install the version for your operating system. After successful installation, run `vagrant --version` in your terminal to see the version number.

### Download the VM Configuration
1. You can download and unzip this file: [FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) This will give you a directory called FSND-Virtual-Machine.
2. Alternately, you can use Github to fork and clone the repository https://github.com/udacity/fullstack-nanodegree-vm.

Either way, you will end up with a new directory containing the VM files. From your terminal, change to this directory with `cd`. Using `ls` list the content of this directory and you will find another directory called vagrant. Change directory to the vagrant directory.

### Start the Virtual Machine
- While you are inside the vagrant subdirectory, run the command `vagrant up`. Vagrant will download the Linux operating system and install it.
- Once `vagrant up` is done with installation, run `vagrant ssh` to log into the Linux VM. 
- You can also run `vagrant status` to check the status of vagrant. 

### Download the application
- You can download the application by clicking on the clone or download button in the repo
- You can as well fork the repo

### Running the application
- In your terminal while vagrant is still running, change diirectory to the Catlog directory. 
- while you are in the catalog directory, run `python application.py`. This will start up the application.
- The application runs on localhost port 5000. Open up your browser and type `http://localhost:5000`. This should take you to the homepage pof the application.
- To be able to use the full functionality of the application like creating category, editing and deleting items, sign in with your google account.
