"""
Plot columns from a Vertica table against one another
"""

# (c) Copyright [2022] Micro Focus or one of its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
import vertica_python

# don't have a display on (this) Unix box
# so will output to fr.png
matplotlib.use('TkAgg')

conn_info = {'host': '127.0.0.1',
             'port': 5433,
             'user': 'dmankins',
             # 'password': 'some_password',
             # 'database': 'a_database',
             # autogenerated session label by default,
             # 'session_label': 'some_label',
             # default throw error on invalid UTF-8 results
             'unicode_error': 'strict',
             # SSL is disabled by default
             'ssl': False,
             # autocommit is off by default
             'autocommit': True,
             # using server-side prepared statements is disabled by default
             'use_prepared_statements': True,
             # connection timeout is not enabled by default
             # 5 seconds timeout for a socket operation (Establishing a TCP connection or read/write operation)
             # 'connection_timeout': 60
             }


def main(argv):
    if len(argv) < 3:
        print(f'{argv[0]}: Usage: {argv[0]} col1 ... table', file=sys.stderr)
        sys.exit(1)

    table = argv[-1]
    cols = argv[1:-1]
        
    cols_for_sql = ", ".join(cols)

    rows = []
    rowcnt = 0
    with vertica_python.connect(**conn_info) as conn:
        cur = conn.cursor()
        # put row_n last so we can use enumerate(cols) later
        cur.execute(f'SELECT {cols_for_sql}, row_n FROM {table}');
        for row in cur.iterate():
            rows.append([float(x) for x in row])
    # toss out the first and last rows because edge effects of the filters
    # a little crazy
    rows = rows[3:-1]
    rowarray = np.array(rows)
    row_n = 0

    fig, axs = plt.subplots(ncols=1, nrows=1)
    fig.suptitle(f'Data from table {table}')
    for n, col in enumerate(cols):
        (cmin, cmax) = (rowarray[:,n].min(), rowarray[:,n].max())
        axs[n].annotate(f'column {col}',
                        # place the text up from th bottom slightly
                        (0, cmin + (cmax - cmin)/10),
                        ha='left', 
                        va='bottom',
                        color='darkgrey')
        axs[n].plot(rowarray[:,n])

    png_name = f'{table}_{"_".join(cols)}_cols.png'
    print(f'Output to {png_name}')
    plt.savefig(png_name)
    plt.show()

if __name__ == '__main__':
    main(sys.argv)
