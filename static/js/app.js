// Delete button handler
$(document).ready(function() {
  $('#del_confirm').hide();
})
$('#del_verify').on('click', function() {
  $(this).hide();
  $('#del_confirm').show();
})

// Toggle Add New element from any page.
$('#ajax_new').on('click', function(e) {
  e.preventDefault();
  $('#a_new_entry').slideToggle();
  $('.all_entries').slideToggle();
})

// Request ajax call to DB for Edit Entry from Detail page.
$('#input-forward').on('click', function(e) {
  e.preventDefault();
  $('#a_new_entry').slideToggle();
  var id = $('#id').text();

  $.ajax({
    method: 'GET',
    url: '/edit-entry/' + id
  }).done(function(response) {
    $('#in-title').val(response.title),
    $('#in-text').val(response.text),
    $('.entry').slideToggle()
  }).fail(function() {
    alert("Shit's brokedededed.")
  })
})

// Submit Edit to the DB and close the 
$("#save_ajax").on("click", function (e) {
  e.preventDefault();

  var id = $("#id").text();
  var title = $("#in-title").val();
  var text = $("#in-text").val();

  $.ajax({
    method: "POST",
    url: "/edit-entry/" + id,
    data: {
        id: id,
        title: title,
        text: text
    }
  }).done(function(response) {
      $("#d_title").html(response.title);
      $("#d_text").html(response.text);
      $(".entry").slideToggle();
    })
    .fail(function() {
      alert( "error" );
    });
});
