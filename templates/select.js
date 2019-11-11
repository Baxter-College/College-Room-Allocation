var data = ""
var display_floor = 1;
var gender = "";

function get_data(inp) {
    data = inp;
}
function get_gender(zid) {
    return data["ZIDS"][zid];
}
function get_rooms(zid) {
    var gender = get_gender(zid);
    if (gender == "m") {
        return data["MALE"]
    } else {
        return data["FEMALE"]
    }
}
function removeElement(elementId) {
    // Removes an element from the document
    var element = document.getElementById(elementId);
    element.parentNode.removeChild(element);
}
function viewFloor(evt, floor) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(floor).style.display = "block";
    evt.currentTarget.className += " active"
}
function validate_form(){
    // TODO: validate the form before send
}