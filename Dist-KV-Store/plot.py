import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
 
abc = pd.DataFrame({'time': [278.77, 288.72, 234.40, 63.96, ],
                    'model': ["Linearizability", "Sequential", "Causal", "Eventual"]})
 
xyz = pd.DataFrame({'time': np.array([158.36, 62.62, 66.01, 63.42,]),
                    'model': ["Linearizability", "Sequential", "Causal", "Eventual"]})
 
plt.plot(abc.model, abc.time, color='blue', label='SET request')
 
plt.plot(xyz.model, xyz.time, color='green', label='GET request')
 
plt.title('Consistency Model vs Time')

plt.xticks(rotation=30, ha='right')
 
plt.legend(loc='upper right')

# Giving x and y label to the graph
plt.xlabel('Consistency Model')
plt.ylabel('Time (milliseconds)')
plt.show()