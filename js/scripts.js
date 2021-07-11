function hideError() {
    var dvAnswer = document.getElementById( "dvError" );
    dvAnswer.innerHTML = "";
    dvAnswer.style.display = "none";
}
function showError(msg) {
    var dvAnswer = document.getElementById( "dvError" );
    dvAnswer.innerHTML = "ERROR: " + msg;
    dvAnswer.style.display = "block";
}

function validate() {
    var toret = false;
    var frmInput = document.getElementById( "frmInput" );
    hideError();

    var name = frmInput[ "name" ].value.trim()

    if ( name.length === 0 ) {
        showError( "debe introducir un nombre." );
    } else {
        toret = true;
    }

    return toret;
}