import React, { Component } from "react";
import { Route, Switch } from "react-router-dom";

import TagList from "./TagList.js"
import New from "./New.js"

/**
 * Tag router for directing between tag list and new
 */
class TagRouter extends Component {
    render(){
        return (
            <div>                
                <Switch>
                    {/* TAG LIST */}
                    <Route exact path={`${this.props.match.url}/`} component={TagList} />
                    
                    {/* NEW */}
                    <Route path={`${this.props.match.url}/new`} component={New} />
                </Switch>
            </div>
        );
    }
}

export default TagRouter;