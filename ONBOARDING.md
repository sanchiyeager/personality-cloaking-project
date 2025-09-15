Getting Started Guide for Our Project
Welcome! Since we are all learning, here is the simple step-by-step process to get your machine ready and contribute to the code.

Step 1: Install the Software
Install Git: Download it from git-scm.com. Just click "Next" through the installer.

Install Python: Download version 3.10 or 3.11 from python.org. IMPORTANT: During installation, CHECK THE BOX that says "Add Python to PATH".

Step 2: Get a Copy of the Code on Your Laptop ("Cloning")
Open your computer's Command Prompt (Windows) or Terminal (Mac/Linux).

Navigate to your Documents or a folder where you want to keep the project. You can use the cd command (e.g., cd Documents).

Type this exact command and press Enter (replace the URL with your actual GitHub repo URL):

bash
git clone https://github.com/your-username/personality-cloaking-project.git
This will create a new folder called personality-cloaking-project. Move into it:

bash
cd personality-cloaking-project
Step 3: Install the Python Libraries We Need
In the same Terminal/Command Prompt (make sure you are inside the personality-cloaking-project folder), run:

bash
pip install transformers torch pandas numpy streamlit
This will install all the necessary AI and data libraries.

Step 4: The Golden Rules of How We Work with Git
We will use a very simple process. Never work directly on the main branch.

For every new task you do (like adding a script, fixing a bug):

Before you start, get the latest code:

bash
git pull origin main
Create a new "branch" for your task. A branch is your own personal sandbox. Name it simply:

bash
git checkout -b add-first-script
# or...
git checkout -b fix-model-error
Do your work. Write your code, save your files.

Send your work to GitHub:

bash
git add .                          # This stages all your changes
git commit -m "Added the first test script"  # This describes what you did
git push origin add-first-script   # This sends your branch to GitHub
Go to our GitHub repository on the website. You will see a button to "Compare & pull request". Click it, create the pull request, and tag @[Your GitHub Username] as a reviewer.

I will review your code and merge it into the main project!

Step 4: Your Role as The "Unblocker"
Schedule a 30-minute "Git & Setup" workshop. Share your screen and walk through the ONBOARDING.md guide live. This is the fastest way to get everyone on the same page.

Be the Gatekeeper: You will be the one reviewing all Pull Requests. This is not just about quality control; it's a teaching moment. You can comment and say, "Great start! Just move this line of code here, then I'll merge it."

Anticipate Problems: The classic beginner error is working directly on the main branch and causing conflicts. When (not if) this happens, don't get frustrated. Help them fix it by showing them how to revert their changes and follow the branch process.

---

###  Team Members

- Pratiksha Choudhuri
- Poonam Kumari
