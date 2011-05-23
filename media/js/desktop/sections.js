var Section = null;

$(document).ready(function() {
    var $body = $('body');
    
    Section = Class.extend({
        init: function(name, transEndTrigger, firstPage) {
            this.name = name;
            this.transEndTrigger = transEndTrigger;
            this.firstPage = firstPage;
            this.currentPage = null;
            this.isChangingPage = false;
        },
        
        hide: function(callback) {
            $body.removeClass(this.name);
            if(this.currentPage) {
                $body.removeClass(this.currentPage);
                this.currentPage = null;
            }
            onTransitionEndOnce($(this.transEndTrigger), callback);
        },
        
        show: function() {
            var self = this;
            this.isChangingPage = false;
            this.currentPage = null;
            $body.addClass(this.name);
            if(this.firstPage) {
                onTransitionEndOnce($(this.transEndTrigger), function() {
                    self.changePage(self.firstPage);
                });
            }
        },
        
        changePage: function(pageName) {
            var self = this,
                doChangePage = function() {
                    $body.addClass(pageName);
                    publish("pagechange", [pageName]);
                    self.isChangingPage = false;
                };
            
            if(pageName !== this.currentPage && !this.isChangingPage) {
                this.isChangingPage = true;
                if(this.currentPage) {
                    $body.removeClass(this.currentPage);
                    onTransitionEndOnce($('#'+this.currentPage), doChangePage);
                } else {
                    doChangePage();
                }
                this.currentPage = pageName;
            }
        }
    });
});