// Toggle Add New element from any page.
$('#ajax_new').on('click', function(e) {
  e.preventDefault();
  $('#a_new_entry').slideToggle();
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
    $('.entry_body').slideToggle()
  }).fail(function() {
    alert("Shit's brokedededed.")
  })
})

// Submit Edit to the DB and close the 


// <form action="{{ request.route_url('add') }}" method="POST" class="add_entry">
//   <label for="title">Title</label>
//   <input id='in-title' type="text" name="title" id="title" required/>
//   <label for="text">Text</label>
//   <textarea id='in-text' name="text" id="text" required></textarea>
//   <input id="submit_ajax" type="submit" value="Submit" name="Submit"/>
// </form>
