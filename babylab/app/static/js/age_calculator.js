// const { default: moment } = await import("moment");
function ms_to_md(diff) {
    let d = Math.floor(diff / (1000 * 60 * 60 * 24));
    let m = Math.floor(d / 30.34);
    d = Math.floor(d % 30.34);
    return [m, d]
}

function ms_to_hm(diff) {
    let m = Math.floor(diff / (1000 * 60));
    let h = Math.floor(m / 60);
    m = Math.floor(m % 60);
    return [h, m]
}

function get_age(date1, date2, units = "md") {
    let d1 = new Date(moment(date1));
    let d2 = new Date(moment(date2));
    let diff = d2 - d1;
    if (units == "md") {
        const [m, d] = ms_to_md(diff)
        return `${m} months, ${d} days`
    }
    if (units == "hm") {
        const [h, m] = ms_to_hm(diff)
        return `${h} hours, ${m} minutes`
    }
}

function get_current_age(timestamp, months, days, units = "md") {
    let today = new Date(moment());
    let t = new Date(moment(timestamp));
    let diff = today - t;

    let m_ms = months * (1000 * 60 * 60 * 24 * 30.34);
    let d_ms = days * (1000 * 60 * 60 * 24);
    const delta = diff + m_ms + d_ms
    console.log(delta)

    if (units == "md") {
        const [m, d] = ms_to_md(delta)
        return `${m} months, ${d} days`
    }
    if (units == "hm") {
        const [h, m] = ms_to_hm(delta)
        return `${h} hours, ${m} minutes`
    }
}

// get_current_age("2025-05-05 17:00", 5, 5)
