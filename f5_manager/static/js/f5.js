function validate_url_mapping_form() {
    var valid = true;
    $("#required_existing_hosts").hide();
    $("#required_url_match").hide();
    $("#required_existing_pool").hide();

    if (!$("input[name='url_match']").val()) {
        valid = false;
        $("#required_url_match").show();
    }

    if ($("input[name='pool_type']:checked").val() == "existing") {
        if (!$("input[name='server_pool']:checked").val()) {
            valid = false;
            $("#required_existing_pool").show();
        }
    }
    else {
        if (!$("input[name='server_pool_member']:checked").val()) {
            valid = false;
            $("#required_existing_hosts").show();
        }
    }
    return valid;
}
