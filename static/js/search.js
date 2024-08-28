$(document).ready(function() {
    $('#search-form').on('submit', function(event) {
        event.preventDefault();
        let keyword = $('#keyword').val();
        let conference = $('input[name="conference"]:checked').val();
        $.ajax({
            url: '/',
            method: 'POST',
            data: { keyword: keyword, conference: conference },
            success: function(response) {
                $('#results').html(response);
            },
            error: function() {
                $('#results').html('<p>エラーが発生しました。</p>');
            }
        });
    });

    $(document).on('click', '.summarize-link', function(event) {
        event.preventDefault();
        let paperId = $(this).data('paper-id');
        $.ajax({
            url: '/summarize',
            method: 'POST',
            data: { paper_id: paperId },
            success: function(response) {
                $('#summary_' + paperId).html(response);
            },
            error: function() {
                $('#summary_' + paperId).html('<p>要約に失敗しました。</p>');
            }
        });
    });
});
