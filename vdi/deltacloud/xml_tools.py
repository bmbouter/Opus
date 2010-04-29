"""An assortment of helper xml functions."""

def xml_get_text(dom, element_name):
    """Gets the text data within the given element.

    It searches the dom object for the elements with the given name.  It hands
    back a list of strings, one string for each element with that name.  For
    example, if dom represents this xml:
        <foo>
            <bar>data1</bar>
            <bar>data2</bar>
        </foo>
    Then xml_get_text() can be used as so:
        >>> xml_get_text(dom, "bar")
        ["data1", "data2"]

    """
    result = []
    for element in dom.getElementsByTagName(element_name):
        text = ""
        for node in element.childNodes:
            if node.nodeType == node.TEXT_NODE:
                text += node.data
        result.append(text)
    return result
    
def xml_get_elements_dictionary(dom, element_name, key_name, value_name):
    """Iterates through a number of elements and generates a dictionary.

    Looks through the dom object for elements of name element_name.  For every
    element it adds an item to the dictionary baised on the element's
    attributes named key and value.

    Suppose dom is an object representing this xml:
        <actions>
          <link rel="reboot" href="http://example.com/reboot"/>
          <link rel="stop" href="http://example.com/stop"/>
        </actions>
   Then xml_get_elements_dictionary can be used as so:
        >>> xml_get_elements_dictionary(dom, "link", "rel", "href")
        {
            "reboot":"",
            "stop":"http://example.com/stop",
        }

    """
    d = {} # 
    for element in dom.getElementsByTagName(element_name):
        key = element.getAttribute(key_name)
        value = element.getAttribute(value_name)
        d[key] = value
    return d
