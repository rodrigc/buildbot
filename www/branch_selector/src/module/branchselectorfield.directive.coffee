# Register new module
class Branchselector extends App
    constructor: -> return [
        'common'
    ]

class Branchselectorfield extends Directive
    constructor: ->
        return {
            replace: false
            restrict: 'E'
            scope: false
            templateUrl: "branchselector/views/branchselectorfield.html"
            controller: '_BranchselectorfieldController'
        }

class _Branchselectorfield extends Controller
    constructor: ($scope, $http) ->
        # HACK: we find the rootfield by doing $scope.$parent.$parent
        rootfield = $scope
        while rootfield? and not rootfield.rootfield?
            rootfield = rootfield.$parent

        if not rootfield?
            console.log "rootfield not found!?!?"
            return

        # copy paste of code in forcedialog, which flatten the fields to be able to find easily
        fields_ref = {}
        gatherFields = (fields) ->
            for field in fields
                if field.fields?
                    gatherFields(field.fields)
                else
                    fields_ref[field.fullName] = field

        gatherFields(rootfield.rootfield.fields)

        # when our field change, we update the fields that we instructed
        $scope.$watch "field.value", (n, o) ->
        
            selector = $scope.field.selectors[n]
            if selector?
                for k, v of selector
                    fields_ref[k].value = v
