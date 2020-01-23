import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch, Redirect} from "react-router-dom";

import Count from "./Count.js";
import Stats from "./Stats.js";

class Maths extends Component {

    render() {
        return (
            
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/count`}>count</Link></li>
                    <li><Link to={`${this.props.match.url}/stats`}>stats</Link></li>
                </ul>

                <Route path={`${this.props.match.url}/count`} render={(props) => <Count {...props} name={this.props.match.params.name}/>} />
                <Route path={`${this.props.match.url}/stats`} render={(props) => <Stats {...props} name={this.props.match.params.name}/>} />
            </div>
        );
    }
}



export default Maths;