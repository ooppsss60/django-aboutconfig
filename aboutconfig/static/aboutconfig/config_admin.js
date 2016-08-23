(function($){$(function(){
    $('.aboutconfig-type-field').change(function() {
        var fieldset = $(this).closest('fieldset');
        var data_field = fieldset.find('[name="value"]');

        if(this.value) {
            $.getJSON(
                this.dataset.url,
                {
                    'id': data_field.attr('id'),
                    'value': data_field.val(),
                    'pk': this.value, // data type id
                    'config_pk': data_field.attr('instance-pk')
                },
                function(data) {
                    data_field.replaceWith(data.content);
                }
            )
        }
    });
});})(django.jQuery);
