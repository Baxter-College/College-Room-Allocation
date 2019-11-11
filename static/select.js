var data = ""
var display_floor = 1;
var gender = "";
console.log("here");
alert("stop");
function get_data(inp) {
    data = inp;
}
function test() {
    console.log("OIK")
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

function validate_form(){
    // TODO: validate the form before send
}


