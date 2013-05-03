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

function validate_offline_form() {
    if (!$("input[name='offline_page']").val()) {
        $("#required_url").show();
        return false;
    }
    return true;
}

function validate_cert_header_form() {
    var is_valid = true;
    $("#required_path").hide();
    $("#required_header").hide();

    if (!$("input[name='path']").val()) {
        $("#required_path").show();
        is_valid = false;
    }
    if (!$("input[name='header']").val()) {
        $("#required_header").show();
        is_valid = false;
    }

    return is_valid;
}
