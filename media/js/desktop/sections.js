var Section = null;

$(document).ready(function() {
    var $body = $('body');
    
    Section = Class.extend({
        init: function(name, transEndTrigger, currentPage) {
            this.name = name;
            this.transEndTrigger = transEndTrigger;
            this.currentPage = currentPage;
        },
        
        hide: function(callback) {
            $body.removeClass(this.name);
            if(this.currentPage) {
                $body.removeClass(this.currentPage);
            }
            onTransitionEndOnce($(this.transEndTrigger), callback);
        },
        
        show: function() {
            var self = this;
            $body.addClass(this.name);
            if(this.currentPage) {
                onTransitionEndOnce($(this.transEndTrigger), function() {
                    $body.addClass(self.currentPage);
                });
            }
        },
        
        changePage: function(pageName) {
            var self = this;
            
            if(pageName != this.currentPage) {
                $body.removeClass(this.currentPage);
                onTransitionEndOnce($('#'+this.currentPage), function() {
                    $body.addClass(self.currentPage);
                });
                this.currentPage = pageName;
            }
        }
    });
});