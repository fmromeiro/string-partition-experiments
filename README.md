# string-partition-experiments
Experiments for exact solutions of the string partition problem using linear programming

Install dependencies by running `pip install -r requirements`. It is recommended to utilize [Python Virtual Env](https://docs.python.org/3/library/venv.html).

To run a subset of the tests, use the executor script. Inform which which implementation to run ('cb', 'cs', 'cb-mod', 'cs-mod'), the indexes of the first and last test and pass the `-r` flag to allow substring reversal.