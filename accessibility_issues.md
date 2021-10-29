# Accessibility checks on solutions-python.ipynb document

Date: 29/10/2021
Tester: RLe
Context: Accessibility checks on Jupyter notebook renderred to HTML using `nbconvert`.
Limitations: Data not included in render. Charts not tested. 

## Issues

* Error: HTML lang value missing - can this be easily set in an ipynb? Is it possible to include your own header html?

* Alert: No page regions or Aria landmarks. Known issue - tolerate.

* Bug: Not flagged as an error or warning, but the ONS logo did not render following `nbconvert`.
Code visible:
<img src="https://datasciencecampus.ons.gov.uk/wp-content/uploads/sites/10/2017/03/data-science-campus-logo-new.svg" alt="ONS Data Science Campus Logo" width = "240" style="margin: 0px 60px" />. 

* Errors: 126 contrast errors. Mostly within code chunks. Can an accessible theme be set? 

* Alert: Redundant link alert on the following code: <a href="../instructions.html#41_Sentiment_Analysis_with_VADER">
instructions
</a>. This means that 2 nearby links within the document point to the same resource. However, I could not find the second link.
Suggest: some light investigation by GD but to tolerate as a false positive if no issue found.

* Alert: Skipped level heading on 'What does our output mean?'. Needs to be a H3.