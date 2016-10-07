// Creates a new administrator via the API
function newAdmin(username, password, name) {

    $.ajax({
        url: '/api/v1/admins',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'username': username,
            'password': password,
            'name': name
        }),

        success: function (response) {
            addStatusMessage('success', 'The administrator was added successfully');
            fillInTable();
        },

        error: function (response) {
            addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
        }
    });
}


// Deletes an administrator via the API
function deleteAdmin(id) {

    $.ajax({
        url: '/api/v1/admins/' + id,
        type: 'delete',

        success: function (response) {
            addStatusMessage('success', 'The administrator was successfully removed');
            fillInTable();
        },

        error: function (response) {
            addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
        }
    });
}

// Unlocks an administrator via the API
function unlockAdmin(id, targetLink) {
  $.ajax({
    url: '/api/v1/admins/unlock/' + id,
    type: 'put',

    success: function (response) {
      addStatusMessage('success', 'The administrator was unlocked successfully');
      targetLink.parent('td').html('Unlocked');
    },

    error: function (response) {
      addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
    }
  });
}

// Disables 2FA for an administrator via the API
function disable2FA(id, targetLink) {
  $.ajax({
    url: '/api/v1/admins/' + id + '/2factor',
    method: 'PUT',
    contentType: 'application/json',
    dataType: 'json',
    data: JSON.stringify({enabled: 'False'}),
    success: function(data){
      addStatusMessage('success', '2FA has been disabled');
      fillInTable();
    },
    error: function (response) {
      addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
    }
  });
}

function configure2FA(id, targetLink) {
}

// Sets the event listeners for x-editable
function editableAdminEventListeners() {

    var adminUsername = $('a.adminUsername');
    var adminPassword = $('a.adminPassword');
    var adminName = $('a.adminName');
    var adminLocked = $('a.adminLocked')
    var admin2FADisable = $('a.admin2FADisable')

    adminUsername.unbind();
    adminPassword.unbind();
    adminName.unbind();
    adminLocked.unbind();
    adminUsername.tooltip();
    adminPassword.tooltip();
    adminName.tooltip();
    adminLocked.tooltip();

    adminUsername.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({ 'username': params.value })
        },

        display: function (value) {
            $(this).html(filterText(value.toLowerCase()));
        },

        error: function (response) {
            addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s username was changed successfully');
        }
    });

    adminPassword.editable({
        type: 'password',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({'password': params.value})
        },

        display: function () {
            $(this).html('●●●●●●●●');
        },

        error: function (response) {
            addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s password was changed successfully');
        }
    });

    adminName.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({ 'name': params.value })
        },

        display: function (value) {
            $(this).html(filterText(value));
        },

        error: function (response) {
            addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s name was changed successfully');
        }
    });

    adminLocked.on('click', function(e) {
        var target = $(e.target);
        unlockAdmin(target.attr('data-pk'), target);
        e.preventDefault();
    });

    admin2FADisable.on('click', function(e) {
        var target = $(e.target);
        bootbox.confirm("Are you sure you want to disable 2-Factor?", function(result) {
          if (result === true) {
            disable2FA(target.attr('data-pk'), target);
          }
        });
        e.preventDefault();
    });
}

// Sets the event listeners in the dynamic table
function adminEventListeners () {

    var twoFAModal = $('#twoFAModal');
    var verify2FABtn = $('#verify2FABtn');
    var deleteModal = $('#deleteModal');
    var deleteModalBtn = $('#modalDeleteBtn');
    var newItemAnchor = $('#newItemAnchor');

    // When hitting the back/forward buttons, reload the table
    $(window).bind("popstate", function () {
        fillInTable();
    });

    // Set the filter event listener
    var typeWatchOptions = {
        callback: function () { fillInTable() },
        wait: 750,
        captureLength: 2
    };

    $('#filterRow input').typeWatch(typeWatchOptions);

    twoFAModal.on('show.bs.modal', function (e) {
      var id = $(e.relatedTarget).data('pk');
      $.ajax({
        url: '/api/v1/admins/' + id + '/2factor/qrcode',
        success: function(data){
           $("#qrcode").html(new XMLSerializer().serializeToString(data.documentElement));
           verify2FABtn.attr('data-pk', id);
        },
        error: function (response) {
          addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
          twoFAModal.modal('hide');
        }
      });
    });

    verify2FABtn.on('click', function (e) {
      var id = $(this).attr('data-pk');
      $.ajax({
        url: '/api/v1/admins/' + id + '/2factor/verify',
        method: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify ({code: $("#verify2FACode").val()}),
        success: function(data){
          twoFAModal.modal('hide');
          fillInTable();
        },
        error: function (response) {
          addStatusMessage('error', filterText(jQuery.parseJSON(response.responseText).message));
        }
      });
    });

    deleteModal.on('show.bs.modal', function (e) {
        deleteModalBtn.attr('data-pk', $(e.relatedTarget).data('pk'));
    });

    deleteModalBtn.on('click', function (e) {
        deleteModal.modal('hide');
        deleteAdmin($(this).attr('data-pk'));
    });

    // When the Add button is clicked, it will POST to the API
    newItemAnchor.on('click', function (e) {

        // Close any status messages
        $('#statusMessage div.alert button').trigger('click');

        var adminInput = $('#newAdminInput');
        var adminPasswordInput = $('#newAdminPasswordInput');
        var adminNameInput = $('#newAdminNameInput');

        // If adminInput is empty, highlight it in red
        if (!adminInput.val()) {
            adminInput.parent().addClass('has-error');
            adminInput.focus();
        }
            // If adminPasswordInput is empty, highlight it in red
        else if (!adminPasswordInput.val()) {
            adminPasswordInput.parent().addClass('has-error');
            adminPasswordInput.focus();
        }
            // If adminNameInput is empty, highlight it in red
        else if (!adminNameInput.val()) {
            adminNameInput.parent().addClass('has-error');
            adminNameInput.focus();
        }
        else {
            // Remove any error bordering on the input fields
            adminInput.parent().removeClass('has-error');
            adminPasswordInput.parent().removeClass('has-error');
            adminNameInput.parent().removeClass('has-error');
            // Create the new user
            newAdmin(adminInput.val(), adminPasswordInput.val(), adminNameInput.val());
            adminInput.val('');
            adminPasswordInput.val('');
            adminNameInput.val('');
            $('#filterRow input').val('');
        }

        e.preventDefault();
    });

    var newAdminInputs = $('#newAdminInput, #newAdminPasswordInput, #newAdminNameInput');
    // When the user clicks out of the errored input field, the red border disappears
    newAdminInputs.blur(function () {
        $('#newAdminInput').parent().removeClass('has-error');
        $('#newAdminPasswordInput').parent().removeClass('has-error');
        $('#newAdminNameInput').parent().removeClass('has-error');
    });

    // When in the input field, this triggers the newItemAnchor when pressing enter
    newAdminInputs.keyup(function (e) {
        var key = e.which;
        if (key == 13) {
            $('#newItemAnchor').trigger('click');
        }
    });
}


// Loads the dynamic table and pagination
function fillInTable () {
    // Set the loading spinner
    manageSpinner(true);

    // If the page or filter was specified, get the appropriate API URL
    apiURL = getApiUrl('admins');

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1;
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            var tableRow = $('#dynamicTableRow' + String(i));
            var html = '';

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-title="Username: "><a href="#" class="adminUsername" data-pk="' + item.id + '" data-url="/api/v1/admins/' + item.id + '" title="Click to change the username">' + filterText(item.username) + '</a></td>\
                    <td data-title="Password: "><a href="#" class="adminPassword" data-pk="' + item.id + '" data-url="/api/v1/admins/' + item.id + '" title="Click to change the password">●●●●●●●●</a></td>\
                    <td data-title="Name: "><a href="#" class="adminName" data-pk="' + item.id + '" data-url="/api/v1/admins/' + item.id + '" title="Click to change the name">' + filterText(item.name) + '</a></td>\
                    <td data-title="2FA: ">' + (item.twoFactor ? ('<a href="#" class="admin2FADisable" data-pk="' + item.id + '" title="Click to disable 2-factor">Configured</a>') : ('<a href="#" class="admin2FAConfigure" data-pk="' + item.id + '" data-toggle="modal" data-target="#twoFAModal" title="Click to configure 2 Factor">Configure</a>')) + '</td>\
                    <td data-title="Locked: ">' + (item.locked ? ('<a href="#" class="adminLocked" data-pk="' + item.id + '" title="Click to unlock the administrator">Locked</a>') : 'Unlocked') + '</td>\
                    <td data-title="Action: "><a href="#" class="deleteAnchor" data-pk="' + item.id + '" data-toggle="modal" data-target="#deleteModal">Delete</a></td>';
            tableRow.length == 0 ? html += '</tr>' : null;
            tableRow.length == 0 ? insertTableRow(html) : tableRow.html(html);

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        result['meta']['pages'] == 0 ? pages = 1 : pages = result['meta']['pages'];
        setPagination(result['meta']['page'], pages, 'admins');
        //Activate x-editable on new elements and other events
        editableAdminEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {
        // Remove the loading spinner
        manageSpinner(false);
        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('admins');
        }
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Sets the default event listeners
    adminEventListeners();

    // Populate the table
    fillInTable();
});
