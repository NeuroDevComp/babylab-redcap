function get_age(birth, test) {
    let date_birth = new Date(date = moment(birth));
    let date_test = new Date(date = moment(test));

    console.log(date_birth)
    console.log(date_test)

    let diff = date_test - date_birth;
    console.log(diff)

    let dd_in_mo = 30.44
    let mo = Math.floor(diff / 1000 / 60 / 60 / 24 / dd_in_mo) % dd_in_mo;
    let dd = Math.floor(diff / 1000 / 60 / 60 / 24) - (mo * dd_in_mo);
    let hh = Math.floor(diff / 1000 / 60 / 60) - (dd * 24);
    let mm = Math.floor(diff / 1000 / 60) % 60 - (mo * 60);

    output = `${mo}mo, ${dd}d, ${hh}h, ${mm}min`
    console.log(output);
    return output
};

