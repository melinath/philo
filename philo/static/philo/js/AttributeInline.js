;(function($){
	var NS = 'attributes'
	var attributesInline = {
		
		init: function () {
			var self = attributesInline,
				attributesWrapper = $('#philo-attribute-entity_content_type-entity_object_id-group'),
				valueTypeFields = $('select[name$="-value_content_type"]'),
				emptyForm = $('.empty-form', attributesWrapper),
				jsonTemplate = $('.row:nth-child(3)'),
				foreignKeyTemplate = $('.row:nth-child(4)'),
				m2mTemplate = $('.row:nth-child(5)');
			
			// remove the fields from the template
			jsonTemplate.detach();
			foreignKeyTemplate.detach();
			m2mTemplate.detach();
				
			valueTypeFields.live('change.'+NS, self.valueTypeChangeHandler);
		},
		
		valueTypeChangeHandler: function (e) {
			var $this = $(this),
				attributeWrapper = $this.closest('*[id^="philo-attribute-"]');
		}
		
	}
	
	$(attributesInline.init);
}(django.jQuery));