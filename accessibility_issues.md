# Accessibility checks on solutions-python.ipynb document

Date: 29/10/2021
Tester: RLe
Context: Accessibility checks on Jupyter notebook renderred to HTML using `nbconvert`.
Limitations: Data not included in render. Charts not tested. 

## Issues

1. Error: HTML lang value missing - can this be easily set in an ipynb? Is it possible to include your own header html?

2. Alert: No page regions or Aria landmarks.This is a known issue with Jupyter Notebook, no action required - tolerate.

3. Bug: Not flagged as an error or warning, but the ONS logo did not render following `nbconvert`.
Code visible:
<img src="https://datasciencecampus.ons.gov.uk/wp-content/uploads/sites/10/2017/03/data-science-campus-logo-new.svg" alt="ONS Data Science Campus Logo" width = "240" style="margin: 0px 60px" />. 
This may be a quirk of the `nbconvert` process. The image renders just fine within the md document here. However the ONS
logo does not render correctly within the output HTML. Action: check the ONS logo renders correctly within the .ipynb and
ignore if no problem found.


4. Errors: 126 contrast errors. Mostly within code chunks. Can an accessible theme be set? 


5. Alert: Redundant link alert on the following code: <a href="../instructions.html#41_Sentiment_Analysis_with_VADER">
instructions
</a>. This means that 2 nearby links within the document point to the same resource. However, I could not find the second link.
Suggest: some light investigation by GD but to tolerate as a false positive if no issue found.

6. Alert: Skipped level heading on 'What does our output mean?'. Needs to be a H3.