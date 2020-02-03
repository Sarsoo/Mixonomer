import React, { Component } from "react";
import { Route, Switch } from "react-router-dom";

import TagList from "./TagList.js"
import New from "./New.js"

class TagRouter extends Component {
    render(){
        return (
            <div>                
                <Switch>
                    <Route exact path={`${this.props.match.url}/`} component={TagList} />
                    <Route path={`${this.props.match.url}/new`} component={New} />
                </Switch>
            </div>
        );
    }
}

export default TagRouter;