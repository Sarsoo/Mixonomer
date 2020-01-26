import React, { Component } from "react";
import { ThemeProvider, Typography } from "@material-ui/core";
import { BrowserRouter as Route, Link} from "react-router-dom";

import GlobalTheme from "../../Theme";

const LazyEdit = React.lazy(() => import("./Edit"))
const LazyCount = React.lazy(() => import("./Count"))


class View extends Component{

    render() {
        return (
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan="2"><h1 className="text-no-select">{ this.props.match.params.name }</h1></th>
                    </tr>
                    <tr>
                        <th colSpan="2">
                            <div>
                                <ul className="navbar" style={{width: "100%"}}>
                                    <li><Link to={`${this.props.match.url}/edit`}>Edit</Link></li>
                                    <li><Link to={`${this.props.match.url}/count`}>Count</Link></li>
                                </ul>
                            </div>
                        </th>
                    </tr>
                </thead>
                <React.Suspense fallback={<LoadingMessage/>}>
                    <Route path={`${this.props.match.url}/edit`} render={(props) => <LazyEdit {...props} name={this.props.match.params.name}/>} />
                    <Route path={`${this.props.match.url}/count`} render={(props) => <LazyCount {...props} name={this.props.match.params.name}/>} />
                </React.Suspense>
            </table>
        );
    }

}

function LoadingMessage(props) {
    return <ThemeProvider theme={GlobalTheme}><Typography variant="h5" component="h2" className="ui-text center-text">Loading...</Typography></ThemeProvider>;
}

export default View;