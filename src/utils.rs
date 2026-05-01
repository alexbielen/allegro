use std::collections::HashSet;
use std::hash::Hash;

/// Returns `true` if every element of `iter` appears exactly once.
pub(crate) fn has_unique_elements<T>(iter: T) -> bool
where
    T: IntoIterator,
    T::Item: Eq + Hash,
{
    let mut uniq = HashSet::new();
    iter.into_iter().all(move |x| uniq.insert(x))
}
