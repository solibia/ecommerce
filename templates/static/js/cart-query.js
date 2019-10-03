<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.2/jquery.min.js"></script>
<script type="text/javascript">
    jQuery(document).ready(function () {
        jQuery('a.query-link').on('click', function (e) {
            e.preventDefault();
            alert();
            jQuery.ajax({
                url: '{% url 'city_of_country' c.id %}',
                method: POST,
                data: {id: jQuery(this).data('id')},
                success: function (data) {
                    jQuery('#dynamic-table').append(data);
                    alert(data)
                }
            })
        })
    })

</script>