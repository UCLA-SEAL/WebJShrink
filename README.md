# WebJShrink
WebJShrink: A Web Service for Debloating Java Bytecode (FSE 2020 Demo)

## Summary
As software projects grow in complexity, they come packaged with under-utilized libraries and therefore become bloated. Though several software debloating tools exist, none of them help developers gain insights into how under-utilized those libraries are nor help developers build conidence in the behavior preservation of software after debloating. To bridge this gap, we developed WebJShrink, a visual analytics tool for analyzing and pruning bloated software projects. WebJShrink is built on JShrink which uses static and dynamic reachability analysis to determine the extent of software bloat. WebJShrink provides rich visualizations of the bloat lurking within a target project’s internal structure. It then removes unused features, and returns a safer, slimmer variant of the software project. To illustrate the target project’s behavior preservation, WebJShrink examines the debloated software with its JUnit tests and visualizes the test results. In evaluating WebJShrink against 26 real world systems, we found WebJShrink could reduce software size by up to 42%, 11% on average, while still passing 100% of unit tests
after debloating. 

## Team
This project was developed by Professor [Miryung Kim](http://web.cs.ucla.edu/~miryung/)'s Software Engineering and Analysis Laboratory.

Please visit [UCLA Java Bytecode Debloating](https://github.com/jdebloat).

https://github.com/jdebloat/jshrink


## How to cite
Please refer to our FSE'20 demo paper, [A Web Service for Debloating Java Bytecode](http://web.cs.ucla.edu/~tianyi.zhang/fse2020-demo-webjshrink.pdf) for more details.

### Bibtex
@inproceedings{10.1145/3368089.3417934,
author = {Macias, Konner and Mathur, Mihir and Bruce, Bobby R. and Zhang, Tianyi and Kim, Miryung},
title = {WebJShrink: A Web Service for Debloating Java Bytecode},
year = {2020},
isbn = {9781450370431},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3368089.3417934},
doi = {10.1145/3368089.3417934},
booktitle = {Proceedings of the 28th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering},
pages = {1665–1669},
numpages = {5},
keywords = {debloating, software optimization, Java bytecode reduction, JShrink},
location = {Virtual Event, USA},
series = {ESEC/FSE 2020}
}

## Video
Please watch an FSE 2020 Demo video [here](https://youtu.be/yzVzcd-MJ1w).
