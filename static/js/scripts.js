$(document).ready(function() {
    $("#reject_id").click(function(){
        var input = `<br><br>
                    <div class="input-group mb-3">
                    <div class="input-group-prepend">
                        <span class="input-group-text" id="inputGroup-sizing-default">Коментарий:</span>
                    </div>
                    <input type="text" name="reject_coment" class="form-control" aria-label="Default" aria-describedby="inputGroup-sizing-default">
                    </div>
                    `
        var button = `<button id='reject_id' type="submit" name="reject" class="btn btn-danger btn-lg btn-block">Отклонить</button>`
        $(this).remove()
        $('#span_reject').append(button);
        $('#span_reject').after(input);
    }); 
});


var option_list = {'verif': 'Только верифицированные', 'non_verif': 'Только не верифицированные', 'under_consideration': 'Только на рассмотрении'}
$( "#category_id" ).change(function() {
  if ($(this).val() == 'helper') {
    $.each(option_list, function(key, value) {
    $('#verefication_id').append('<option value="' + key + '">' + value + '</option>');
  });
} else {
    $.each(option_list, function(key, value) {
    $('#verefication_id option[value=' + key + ']').remove();
  });
}
});

var option_list_sort = {'asc': 'По возрастанию', 'desc': 'По убыванию'}
$( "#sort_id" ).change(function() {

  if ($(this).val() != '') {
    $.each(option_list_sort, function(key, value) {
    $('#sort_params_id option[value=' + key + ']').remove();
    $('#sort_params_id').append('<option value="' + key + '">' + value + '</option>');
  });
  } else {
    $.each(option_list_sort, function(key, value) {
    $('#sort_params_id option[value=' + key + ']').remove();
  });
  }
});