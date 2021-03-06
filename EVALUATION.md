# Credentials

To evaluate participants and update the leaderboard, you'll need the following credentials:

 - write access to https://github.com/calculquebec/magic-castle-neurips
 - write access to https://github.com/ds4dm/www.ecole.ai
 - an account on the cluster: https://ml4co.calculquebec.cloud
 - the following google sheet (public): https://docs.google.com/spreadsheets/d/1YrKlKggEoBzH3WNRglUyPgFDAZEoZDBcbED-cV2WtHU/edit?usp=sharing

# 1. Reserve the compute ressources

To save computing ressources, we keep the number of compute nodes in
the cluster to 0, and we request additional nodes only when needed.

The evaluation of each team is plit into three jobs, one for each problem benchmark.
Hence, to evaluate `N` submissions in parallel we should request at most `3*N` compute nodes.

Changing the number of compute nodes reserved to the cluster boils down to
editing a single configuration file. This can be made directly using github's GUI:
https://github.com/calculquebec/magic-castle-neurips/blob/master/main.tf

To get, for example, 6 compute nodes, change line 20 of that file from
```hcl
    node   = { type = "g1-8gb-c4-22gb", tags = ["node"], count = 0 }
```
to:
```hcl
    node   = { type = "g1-8gb-c4-22gb", tags = ["node"], count = 6 }
```

Wait about 30 minutes for the changes to take effect.

# 2. Set up your environment

Connect to the cluster via SSH:
```
ssh gassmaxi@ml4co.calculquebec.cloud
```

First, you can check the number of nodes available in the cluster with `sinfo`
```bash
[gassmaxi@login1 ml4co-competition]$ sinfo
PARTITION          AVAIL  TIMELIMIT  NODES  STATE NODELIST
cpubase_bycore_b1*    up   infinite      6   idle node1
```

If the number of requested nodes does not show up yet, you can still process and
set up the environment while waiting.

## Set up bashrc

Execute those commands in the shell, and also put them in your `~/.bashrc` file

```bash
umask 000  # create new files with default read-write permission for all
export SINGULARITY_CACHEDIR="$HOME/scratch/.singularity/cache"
export SINGULARITY_TMPDIR="$HOME/scratch/.singularity/tmp"
export PIP_CACHE_DIR="$HOME/scratch/.cache/pip"
```

# 3. Collect the team submissions

Place yourself in the project directory
```
cd /project/def-sponsor00/ml4co-competition
```

Before doing anything, make sure that the previous evaluations
have been cleaned up, and the submissions evaluated in the previous round
(the three folders `primal`, `dual` and `config`) have been placed into a folder
under `submissions/_previous_rounds/MONTH_DAY` corresponding to the last time
the leaderboard was updated. You can find that information on the
[leaderboard page](https://www.ecole.ai/2021/ml4co-competition/#leaderboard).

Submissions are received in the email box
`ml4co.competition@gmail.com`. To keep things manageable at the moment only
three persons have access the email box: Maxime, Justin and Lara. Reach out to them
to collect the submission files to be evaluated.

**Important**: keep track of everything you do (teams collected, teams evaluated etc.)
in the [google spreadsheet](https://docs.google.com/spreadsheets/d/1YrKlKggEoBzH3WNRglUyPgFDAZEoZDBcbED-cV2WtHU/edit?usp=sharing)
under the _Teams_ tab.

Download the submissions of the teams you want to evaluate on your local
machine. Note also the additional information that participants are
supposed to send along with their submission. For example:
```
name of your team: nf-lzg
task(s) in which you are competing: dual
whether your code requires a GPU or not to run: no
whether your team is composed only of students or not: yes
```

Rename the submitted archive file so that it matches the team name.
For example, here `submission.zip` should be renamed to `nf-lzg.zip`.

Depending on the task in which the team competes, place the archive file
in the correct sub-folder within `submissions/`. For example, if the received submission
concerns the dual task, place the file in `submissions/dual/`.

Extract the submitted file somewhere, and make sure that it consists of
a single folder named after the team name. It should contain at least
the following files:
```
TEAM_NAME/conda.yaml
TEAM_NAME/init.sh
TEAM_NAME/agents/primal.py (if team competes in the primal task)
TEAM_NAME/agents/dual.py (if team competes in the dual task)
TEAM_NAME/agents/config.py (if team competes in the config task)
```

Finally, place the team's folder along with the team's archive file. For example, if the received submission
concerns the dual task, place the file in `submissions/dual/`.
```
[gassmaxi@login1 ml4co-competition]$ ls submissions/dual/ -l
total 2352
drwxr-xr-x. 4 gassmaxi def-sponsor00     66 Sep 17 18:28 ark
-rw-r--r--. 1 gassmaxi def-sponsor00   4717 Sep 17 03:07 ark.zip
drwxrwxr-x. 3 gassmaxi def-sponsor00    179 Sep 17 18:39 EI-OROAS
-rw-r--r--. 1 gassmaxi def-sponsor00 729672 Sep 17 02:52 EI-OROAS.zip
drwxr-xr-x. 4 gassmaxi def-sponsor00     84 Sep 17 18:39 gentlemenML4CO
-rw-r--r--. 1 gassmaxi def-sponsor00 260982 Sep 17 03:13 gentlemenML4CO.zip
drwxrwxr-x. 3 gassmaxi def-sponsor00    100 Sep 17 02:38 Nuri
-rw-r--r--. 1 gassmaxi def-sponsor00 667041 Sep 17 02:35 Nuri.zip
drwxrwxr-x. 4 gassmaxi def-sponsor00     66 Sep 17 03:03 qqy
-rw-r--r--. 1 gassmaxi def-sponsor00   4507 Sep 17 02:57 qqy.zip
drwxrwxr-x. 3 gassmaxi def-sponsor00    206 Sep  9 00:49 uofx
-rw-r--r--. 1 gassmaxi def-sponsor00 728054 Sep 17 02:31 uofx.zip
```

# 4. Check that the team submissions are legit

In the `conda.yaml` file, make sure the proper python / ecole / scip versions are used
```
  - python=3.7
  - scip=7.0.3
  - ecole=0.7.3
```

In the `init.sh` file, make sure the participants do not alter the
python / ecole / scip versions installed with the environment. Try to
look also for anything suspicious in that file (e.g., participants
should not try to upload any kind of data to the internet).

# 5. Submit the evaluation jobs

Edit the file `01_run_evaluations.sh`, and add (or uncomment) the three
lines which correspond to the team and task you want to evaluate. For example, for team `nf-lzg`
which competes in the dual task, those lines are:
```bash
sbatch scripts/run_evaluation.sh nf-lzg dual item_placement partial
sbatch scripts/run_evaluation.sh nf-lzg dual load_balancing partial
sbatch scripts/run_evaluation.sh nf-lzg dual anonymous partial
```
Make sure that all other lines in that file are commented.

Finally, submit the evaluation jobs
```
source 01_run_evaluations.sh
```

You can check that the jobs' status with the sq command
```bash
[gassmaxi@login1 ml4co-competition]$ sq
          JOBID     USER      ACCOUNT           NAME  ST  TIME_LEFT NODES CPUS TRES_PER_N MIN_MEM NODELIST (REASON) 
            289 gassmaxi def-sponsor0 run_evaluation   R 1-05:59:59     1    1        N/A     20G node1 (None) 
            290 gassmaxi def-sponsor0 run_evaluation  PD 1-06:00:00     1    1        N/A     20G  (Resources) 
            291 gassmaxi def-sponsor0 run_evaluation  PD 1-06:00:00     1    1        N/A     20G  (Priority)
```

**Important**: keep track of the jobs you run, along with which team / task / problem benchmark they correspond to
in the [google spreadsheet](https://docs.google.com/spreadsheets/d/1YrKlKggEoBzH3WNRglUyPgFDAZEoZDBcbED-cV2WtHU/edit?usp=sharing)
under the _Jobs_ tab.

# 6. Babysit the jobs

Make sure everything goes alright.

For intermediate evaluations, the expected runtime for each job is about:
 - 20x5 = 100 minutes (1h40) for the primal task
 - 20x15 = 300 minutes (5h) for the dual and the config tasks

For the final evaluation, the expected runtime for each job is about:
 - 100x5 = 500 minutes (8h20) for the primal task
 - 100x15 = 1500 minutes (25h) for the dual and the config tasks

When all jobs are completed, they should not appear anymore in the queue:
```bash
[gassmaxi@login1 ml4co-competition]$ sq
          JOBID     USER      ACCOUNT           NAME  ST  TIME_LEFT NODES CPUS TRES_PER_N MIN_MEM NODELIST (REASON) 
```

The status of each job can be checked individually with `seff JOBID`. For example,
here is the status of job 289 after completion:
```
[gassmaxi@login1 ml4co-competition]$ seff 289
Job ID: 289
Cluster: ml4co
User/Group: gassmaxi/gassmaxi
State: COMPLETED (exit code 0)
Cores: 1
CPU Utilized: 04:51:53
CPU Efficiency: 94.89% of 05:07:36 core-walltime
Job Wall-clock time: 05:07:36
Memory Utilized: 1.08 GB
Memory Efficiency: 5.41% of 20.00 GB
```

Each job produces a log file, `logs/run_evaluation_JOBID.out`. Unfortunately this file
is not written in real-time (buffer), so its content might appear empy until the job finishes.
After the successful completion of a job, this log file should contain the output of the team's
initialization script (conda outputs mostly), and the final part should contain the output of the
evaluation itself, for the 20 instances evaluated (100 instances in the final evaluation).
For example, for job 289:
```bash
[gassmaxi@login1 ml4co-competition]$ head -n 5 logs/run_evaluation_289.out 
TEAM=nf-lzg
TASK=dual
BENCHMARK=item_placement
EVALUATION=partial
Cloning into '.'...
```
```bash
[gassmaxi@login1 ml4co-competition]$ tail -n 6 logs/run_evaluation_289.out 
Instance item_placement_10019.mps.gz
  seed: 19
  initial primal bound: 582.6603805870014
  initial dual bound: 2.7173101770000256
  objective offset: 0
  cumulated reward (to be maximized): 3420.333923344073
```

Finally, if everything goes allright, each job should produce a CSV file with
the results of the team. For example, for job 289:
```bash
[gassmaxi@login1 ml4co-competition]$ cat results/partial/nf-lzg/dual/1_item_placement.csv
instance,seed,initial_primal_bound,initial_dual_bound,objective_offset,cumulated_reward
../../instances/1_item_placement/test/item_placement_10000.mps.gz,0,586.8111255119967,5.4059507480000075,0,8470.832700248262
../../instances/1_item_placement/test/item_placement_10001.mps.gz,1,585.0918695782982,2.858140179300038,0,3530.942670553831
../../instances/1_item_placement/test/item_placement_10002.mps.gz,2,740.3138893089987,2.1398628850001025,0,2177.643168032206
../../instances/1_item_placement/test/item_placement_10003.mps.gz,3,612.3853851310005,5.0419567770001015,0,6854.904463063807
../../instances/1_item_placement/test/item_placement_10004.mps.gz,4,542.0065967900038,0.5984374850000271,0,600.8856591807873
../../instances/1_item_placement/test/item_placement_10005.mps.gz,5,524.6245861799956,2.7498155400000264,0,3295.600139424367
../../instances/1_item_placement/test/item_placement_10006.mps.gz,6,599.81944828,3.641006420000053,0,4367.992974059467
../../instances/1_item_placement/test/item_placement_10007.mps.gz,7,519.6799417739987,4.28538823000001,0,5191.367113856184
../../instances/1_item_placement/test/item_placement_10008.mps.gz,8,638.8700493169972,3.5950156570000344,0,6300.799496710244
../../instances/1_item_placement/test/item_placement_10009.mps.gz,9,643.6093315759999,0.0,0,139.34587524331587
../../instances/1_item_placement/test/item_placement_10010.mps.gz,10,628.4794442330009,10.923102526000154,0,10656.785602908552
../../instances/1_item_placement/test/item_placement_10011.mps.gz,11,626.3987464701058,6.965796413100065,0,12900.703769237061
../../instances/1_item_placement/test/item_placement_10012.mps.gz,12,672.9141671300001,5.492216029000227,0,6730.196511156417
../../instances/1_item_placement/test/item_placement_10013.mps.gz,13,632.0308769806994,0.38291618170003355,0,345.21626496062856
../../instances/1_item_placement/test/item_placement_10014.mps.gz,14,578.1204922600006,1.089210420000024,0,1318.0044719589703
../../instances/1_item_placement/test/item_placement_10015.mps.gz,15,665.6448123559977,1.19446729299999,0,1198.3521589932127
../../instances/1_item_placement/test/item_placement_10016.mps.gz,16,685.2467454981104,1.9416003080000883,0,2087.076319276331
../../instances/1_item_placement/test/item_placement_10017.mps.gz,17,672.0819276939974,3.0073285070000657,0,5523.980823809572
../../instances/1_item_placement/test/item_placement_10018.mps.gz,18,558.9391078520042,3.261200011671449e-05,0,0.029351027474603178
../../instances/1_item_placement/test/item_placement_10019.mps.gz,19,582.6603805870014,2.7173101770000256,0,3420.333923344073
```

# 7. Produce the result tables

If the team is composed only of students, add the team name to the student teams list in the
`scripts/print_results.py` file, line 10:
```python
student_teams = [
    "Nuri",
    "qqy",
    "nf-lzg",
    ...
]
```

Run the script that produces the HTML tables with the results
```bash
source 01_print_results.sh
```

Look at the produced tables, and check that they are ok. The script should produce two files with three tables each (one per task):

- `results.html`: the global leaderboard
- `results_students.html`: the leaderboard for student teams


# 8. Update the leaderboard

## Option 1: edit and test the website locally

Install github-pages on your local machine, by following
https://kbroman.org/simple_site/pages/local_test.html
The install commands should basically be
```bash
gem install github-pages
gem update github-pages
```

Clone the competition's website repo, and run the website:
```bash
git clone git@github.com:ds4dm/www.ecole.ai.git
cd www.ecole.ai
jekyll build --watch & jekyll serve
```

Open http://localhost:4000/2021/ml4co-competition/#leaderboard in a browser to
see the current version of the leaderboard.

Update the leaderboard tables, by erasing the previous tables in `index.html` file (line 1207)
and replacing them with the contents of `results.html` and `results_students.html` (copy-pasting).
```html
                <h3>Student leaderboard</h3>
Primal task
<table>
    <thead>
...
```

Update the *last update* information in `index.html` (line 998)
```html
				Last update: August 19th.
```

Commit and push the changes to make them visible on the online website.

Chech the leaderboard online https://www.ecole.ai/2021/ml4co-competition/#leaderboard

## Option 2: update the website directly through github

Or, use the github GUI to directly update the main website:
https://github.com/ds4dm/www.ecole.ai/blob/master/2021/ml4co-competition/index.html

# 9. Release the compute ressources

Finally, release the compute nodes if no evaluation remains to be done.
This can be done directly using github's GUI:
https://github.com/calculquebec/magic-castle-neurips/blob/master/main.tf

To get 0 compute nodes, change line 20 to:
```hcl
    node   = { type = "g1-18gb-c4-22gb", tags = ["node"], count = 0 }
```

# 10. Clean up the processed submissions

Move the three folders containing the submissions that you've evaluated
(`submissions/primal`, `submissions/dual`, `submissions/config`) into a backup folder,
under `submissions/_previous_rounds/MONTH_DAY` corresponding to the leaderboard update
you just did.

Also, copy-paste the team results that were used to build the leaderboard
(`results/partial/*`) into a backup folder, under `results/_previous_rounds/MONTH_DAY`
corresponding to the leaderboard update you just did.

# 11. Send the official annoucement

First, write an annoucement in the [discussions](https://github.com/ds4dm/ml4co-competition/discussions),
with the `annoucement` tag. You can simply copy-paste one of the previous annoucements (e.g., New results: October 8th),
and add in additional information for this week's evaluations if any.

Second, copy-paste this announcement into an email that you'll send from the `ml4co.competition@gmail.com`
account. As a title I usually use something like `[NeurIPS 2021 ML4CO competition] New results: October 8th`.
Then, copy the list of all registered participants from the [registration form](https://docs.google.com/spreadsheets/d/1ScdUEtoJoj-WufgU-e3VPH0huHkZN2UJdV8S-JVp7Sg/edit?usp=sharing), and paste it into the BCC field (**not in the CC field!**
Otherwise we disclose the whole list of participants to everyone). You can also include the list of all the organizers, in BCC again. I do that by hand:
```
Maxime Gasse <maxime.gasse@polymtl.ca>,
Andrea Lodi <andrea.lodi@polymtl.ca>,
Sebastian Pokutta <pokutta@zib.de>,
Pawel Lichocki <pawell@google.com>,
Miles Lubin <miles.lubin@gmail.com>,
"Papageorgiou, Dimitri J" <dimitri.j.papageorgiou@exxonmobil.com>,
Simon Bowly <Simon.Bowly@monash.edu>,
Chris Cameron <cchris13@cs.ubc.ca>,
Quentin Cappart <quentin.cappart@polymtl.ca>,
Jonas Charfreitag <jcharfreitag@cs.uni-bonn.de>,
Didier Ch??telat <didier.chetelat@polymtl.ca>,
Justin Dumouchelle <dumouchelle.justin@polymtl.ca>,
Ambros Gleixner <gleixner@zib.de>,
Aleksandr Kazachkov <akazachk@gmail.com>,
Elias Khalil <khalil@mie.utoronto.ca>,
Christopher Morris <christopher.morris@tu-dortmund.de>,
Antoine Prouvost <antoine.prouvost@polymtl.ca>,
Lara Scavuzzo <lascavuzzo@gmail.com>,
augustin.parjadis-de-lariviere@polymtl.ca,
Quentin Cappart <quentin.cappart@gmail.com>,
Antonia Chmiela <chmiela@zib.de>,
Christoph Graczyk <graczyk@zib.de>
```


# Additional ressources

How to use compute-canada:
https://docs.computecanada.ca/wiki/Running_jobs/en
