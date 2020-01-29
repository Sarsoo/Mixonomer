import React, { Component } from "react";
import { BrowserRouter as Route} from "react-router-dom";

import Count from "./Count.js";

class Maths extends Component {

    render() {
        return <Route path={`${this.props.match.url}/count`} render={(props) => <Count {...props} name={this.props.match.params.name}/>} />;
    }
}



export default Maths;