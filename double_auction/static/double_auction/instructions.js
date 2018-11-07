var cwas = new Vue({
    el: '#cont1',
    data: {
        active: errorExists ? 2 : 0 
    },
    methods: {
        next: function() {
            this.active+=1
            document.body.scrollTop = 0; // For Safari
            document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
        },
        back: function() {
            this.active-=1
            document.body.scrollTop = 0; // For Safari
            document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
        }
    }
})
