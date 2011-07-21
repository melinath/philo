;(function($){
	var NS = 'attributes'
	var attributesInline = {
		
		init: function () {
			var self = attributesInline,
				attributesWrapper = $('#philo-attribute-entity_content_type-entity_object_id-group'),
				valueTypeFields = $('select[name$="-value_content_type"]');
				
			valueTypeFields.bind('change.'+NS, self.valueTypeChangeHandler);
		},
		
		valueTypeChangeHandler: function (e) {
			var $this = $(this),
				attributeWrapper = $this.closest('*[id^="philo-attribute-"]');
			// TODO: actually implement this. We'll need an API for some degree of server-side interaction first.
		}
		
	}
	
	$(attributesInline.init);
}(django.jQuery));