import re
from . import util

def convertHeadings(entry):
    # Regex to find all large headings in an entry
    # Match all lines starting with '#' ('^' in multiline mode means start of a new line)
    headings = re.findall("^#.*?$", entry, re.MULTILINE)
    for heading in headings:

        # Replace markdown syntax with html tags
        # Skip hashes and remove leading / trailing whitespaces
        if heading.startswith("######"):
            convertedHeading = re.sub(heading, "<h6>" + heading[6:].strip() + "</h6>", heading)
        elif heading.startswith("#####"):
            convertedHeading = re.sub(heading, "<h5>" + heading[5:].strip() + "</h5>", heading)
        elif heading.startswith("####"):
            convertedHeading = re.sub(heading, "<h4>" + heading[4:].strip() + "</h4>", heading)
        elif heading.startswith("###"):
            convertedHeading = re.sub(heading, "<h3>" + heading[3:].strip() + "</h3>", heading)
        elif heading.startswith("##"):
            convertedHeading = re.sub(heading, "<h2>" + heading[2:].strip() + "</h2>", heading)
        elif heading.startswith("#"):
            convertedHeading = re.sub(heading, "<h1>" + heading[1:].strip() + "</h1>", heading)

        # Replace the heading in the entry
        # '(?m)^' is syntax for multiline mode in re.sub()
        entry = re.sub("(?m)^"+heading, convertedHeading, entry, re.MULTILINE)

    return entry

def convertBoldTexts(entry):
    # Bold texts start and end with '**' or '__'
    boldTexts = re.findall("(?:\*\*.*?\*\*)|(?:__.*?__)", entry)
    for boldText in boldTexts:
        convertedBoldText = re.sub(re.escape(boldText), "<b>" + boldText[2:-2] + "</b>", boldText)
        entry = re.sub(re.escape(boldText), convertedBoldText, entry)

    return entry

def convertUnorderedLists(entry):
    # Unordered lists start with '*' or '-' on a new line
    # and end when the following line doesn't start with '*' or '-'
    unorderedLists = re.findall("(^(?:\*|-)(?:.|\s)*?(?=^(?!(?:\*|-))))", entry, re.MULTILINE)
    for unorderedList in unorderedLists:

        # Add <ul> tag to the unordered list
        convertedUnorderedList = re.sub(re.escape(unorderedList), "<ul>\n" + unorderedList + "</ul>\n", unorderedList)
        entry = re.sub(re.escape(unorderedList), convertedUnorderedList, entry)

        # Add <li> tags to every element (line) of the unordered list
        listElementPattern = "^(?:\*|-).*?$"
        listElements = re.findall(listElementPattern, unorderedList, re.MULTILINE)
        for listElement in listElements:
            convertedListElement = re.sub(re.escape(listElement), "<li>" + listElement[1:].strip() + "</li>", listElement)
            entry = re.sub(re.escape(listElement), convertedListElement, entry)

    return entry

def convertLinks(entry):
    # Find all links in form '[text](url)'
    links = re.findall("\[.*?\]\(.*?\)", entry)
    for link in links:
        # Split into text and url and convert the link
        text = re.search("\[(.*?)\]", link)
        text = text.group(1)
        url = re.search("\((.*?)\)", link)
        url = url.group(1)
        convertedLink = re.sub(re.escape(link), "<a href='" + url + "'>" + text + "</a>", link)
        entry = re.sub(re.escape(link), convertedLink, entry)

    return entry

def convertParagraphs(entry):
    # Paragraphs start at beginning of the string or after two line breaks
    # and end before two line breaks or end of the string
    # '[^0-9#\-][^\.\*]' is to handle cases of markdown syntax
    paragraphs = re.findall("(?:\r\n\r\n|\r\r|\n\n|^)([^0-9#\-<][^\.\*].*?)(?=$|\r\n\r\n|\r\r|\n\n)", entry)
    print(paragraphs)
    for paragraph in paragraphs:
        convertedParagraph = re.sub(re.escape(paragraph), "<p>" + paragraph + "</p>", paragraph)
        entry = re.sub(re.escape(paragraph), convertedParagraph, entry)
    print(entry)
    return entry