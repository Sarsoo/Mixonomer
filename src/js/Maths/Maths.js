import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch, Redirect} from "react-router-dom";

import Count from "./Count.js";

class Maths extends Component {

    render() {
        return (
            
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/count`}>count</Link></li>
                </ul>

                <Route path={`${this.props.match.url}/count`} render={(props) => <Count {...props} name={this.props.match.params.name}/>} />
            </div>
        );
    }
}



export default Maths;