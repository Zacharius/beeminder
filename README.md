A place for experiments and scripts with the beeminder api.

Auto Incrementer

A script to auto increment beeminder goals if they meet several criteria

To run it you would first put your username, token, and a list of goals in a file called vars.py. A file called vars.example.py exists to give you an example of the form it should have.

Each goal value should look like the below:

    {"name": 'bed', "step_rate": .5, "rate_limit": 6, "buffer_threshold": 3}

- name :: name of beeminder goal
- step_rate :: how much to add(or subtract) from the rate
- rate_limit :: When rate reaches this, stop incrementing
- buffer_threshold :: must have this many days of buffer before incrementing goal

The program will check every goal that you provide and increment it the goal meets the following conditions:

- It is a Do More or Do Less type goal
- your actual rate over the last period is greater than your set rate
- Number of buffer days is greater than buffer_threshold
- set rate is less that rate_limit(or more for Do Less goals)

Once that is set up just run from the base directory where you cloned the repo
  
    python auto_incrementer.py
