var detailKey, snippet;

$(function Render() {
  if (window.location.href.indexOf('index') > -1) {
    $postsEl = $('.posts-short');
    for (var key in localStorage) {
      var snippet = JSON.parse(localStorage.getItem(key));
      if (snippet.title) {
        $postsEl.append('<section id=' + key + '><h1 class="snippets">' + snippet.title + '</h1><h3>' + snippet.date + '</h3></section>');
      }
    }
    $('.snippets').on('click', function(e) {
      e.preventDefault();
      var $localKey = JSON.stringify($(this).parent().attr('id'));
      localStorage.setItem('id-key', $localKey);
      window.location.href = 'detail.html';
    })
  }
  else if (window.location.href.indexOf('new-entry') > -1) {
    $('#submit-new').on('click', function(e) {
      e.preventDefault();
      var new_post = {};
      new_post['title'] = $('#in-title').val();
      new_post['text'] = $('#in-text').val();
      new_post['author'] = $('#in-author').val();
      new_post['date'] = $('#in-date').val();
      var jsonObj = JSON.stringify(new_post);
      
      if (new_post['title'].indexOf(' ') >= 0) {
        var slug = new_post['title'];
        var new_id = slug.toLowerCase().replace(/ /g,'-').replace(/[^\w-]+/g,'')
      }

      localStorage.setItem(new_id + new_post['date'], jsonObj);
      window.location.href = 'index.html';
    });
  }
  else if (window.location.href.indexOf('detail') > -1) {
    var $postsEl = $('.posts-full');
    var $id = $(this).attr('id');
    var detailKey = JSON.parse(localStorage.getItem('id-key'));
    var snippet = JSON.parse(localStorage.getItem(detailKey));
    $postsEl.append('<section><h1>' + snippet.title + '</h1><h3>' + snippet.date + '</h3><h3><author>' + snippet.author + '<p>' + snippet.text + '</p><button id="edit">Edit</button><button id="delete">Delete</button></section>');

    $('#edit').on('click', function() {
      window.location.href = 'edit-entry.html';
    });

    $('#delete').on('click', function() {
      localStorage.removeItem(detailKey);
      window.location.href = 'index.html';
    });
  }
  else if (window.location.href.indexOf('edit-entry') > -1) {
    var detailKey = JSON.parse(localStorage.getItem('id-key'));
    var snippet = JSON.parse(localStorage.getItem(detailKey));
    $('#edit-title').val(snippet.title);
    $('#edit-text').val(snippet.text);
    $('#edit-author').val(snippet.author);
    $('#edit-date').val(snippet.date);
    $('#edit-title').prop('disabled', true);
    $('#edit-author').prop('disabled', true);
    $('#edit-date').prop('disabled', true);

    $('#cancel').on('click', function(e) {
      e.preventDefault();
      window.location.href = 'detail.html';
    });
    $('#submit-edit').on('click', function(e) {
      e.preventDefault();
      var detailKey = JSON.parse(localStorage.getItem('id-key'));
      var snippet = JSON.parse(localStorage.getItem(detailKey));
      snippet.text = $('#edit-text').val()
      var jsonObj = JSON.stringify(snippet);
      localStorage.setItem(detailKey, jsonObj);
      window.location.href = 'detail.html';
    })
  }
});



