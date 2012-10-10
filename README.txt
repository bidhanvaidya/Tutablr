
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

Local = your local copy of the files
Origin = the server (bitbucket) copy of the files

1. Everyone needs their own BRANCH of this project.
        - git branch <your_name>_<branch_details>_branch
        - git checkout <branch-name>

2. For Example: if Ashwin wanted to do Rregistration work and Messaging work on two different branches, he would create two branches as such.
        - git checkout master (this gets the main branch)
        - git branch ashwin_registration_branch (creates a branch of that name)
        - git branch ashwin_messaging_branch (see above)
        - git checkout ashwin_registration_branch ( go to the registration branch you created)

3. NO ONE IS TO COMMIT ONTO MASTER or ORIGIN/MASTER without telling the rest of the group. 
4. NO ONE IS TO COMMIT TO ANYONE ELSE'S BRANCHES locally or on ORIGIN

5. Any questions regarding merging etc. ask Ashwin (ashwin@freelancer.com)


*********************************************
**                  Folder Structure of Tutablr              **
*********************************************

<Your Folder>
|____<Virtualenv Environment Folder>
|____tutablr
           |____tutablr <--- this is where settings.py etc. is stored
           |____tutablr_app <--- this is the main application


*********************************************
**                        Useful Tutorial Links                   **
*********************************************
        - Dajaxice: 
        - Ajax in Django:  http://www.pythondiary.com/tutorials/django-and-ajax-dajaxice.html
        - Django Registration: 
        - South (Database Management):
