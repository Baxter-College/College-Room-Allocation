var data = {{ data }};

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
function validate_form(){
    // TODO: validate the form before send
}