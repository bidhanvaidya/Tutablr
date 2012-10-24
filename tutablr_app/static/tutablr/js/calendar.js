
            $("#add_unavailable").submit(function() {

                var url = "/../../add_unavailable/";
                // the script where you handle the form input.

                $.ajax({
                    type : "POST",
                    url : url,
                    data : $("#add_unavailable").serialize(), // serializes the form's elements.
                    success : function(data) {
                        return true;
                        // show response from the php script.
                    }
                });

                return false;
                // avoid to execute the actual submit of the form.
            });
