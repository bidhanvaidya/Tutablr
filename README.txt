
************************************************************************************
******                                                    TUTABLR DOCUMENTATION                                        ******
************************************************************************************

**************************************
**              Installation of Packages         **
**************************************

1. Create a folder. 
2. Change Directory into folder ("cd <folder_name>")
3. Install Virtualenv
4. Create Virtualenv environment
5. Inside the environment:
        - install django 1.4.1 (pip install django)
        - install South (easy_install South)
        - install django-registration (pip install django-registration)
6. Clone this repository 


**************************************
**             Setting Up the Database         **
**************************************

Understand that we are not using manage.py syncdb to do the model syncing.
We are using South. 


*********************************************
**             How to use GIT with this Project         **
*********************************************

1. Everyone needs their own BRANCH of this project.
        - git branch <your_name>_<branch_details>_branch
        - git checkout <branch-name>

*********************************************
**                  Folder Structure of Tutablr              **
*********************************************

<Your Folder>
|____<Virtualenv Environment Folder>
|____tutablr
           |____tutablr <--- this is where settings.py etc. is stored
           |____tutablr_app <--- this is the main application
