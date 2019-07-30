import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch, Redirect} from "react-router-dom";

import ChangePassword from "./ChangePassword.js"

class Settings extends Component {

    render() {
        return (
            <div>
                <ul className="navbar" style={{width: "100%"}}>
                    <li><Link to={`${this.props.match.url}/password`}>password</Link></li>
                </ul>
                
                <Route path={`${this.props.match.url}/password`} component={ChangePassword} />

            </div>
        );
    }
}



export default Settings;